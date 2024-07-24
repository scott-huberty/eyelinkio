from datetime import timedelta, timezone
from pathlib import Path
from warnings import warn

import numpy as np

from ..edf import _defines
from .check import _check_mne_installed, _check_pandas_installed


def _get_test_fnames():
    """Get usable test files (omit EDF if no edf2asc)."""
    path = Path(__file__).parent.parent / "tests" / "data"
    fnames = sorted(list(path.glob("*.edf")))  # test_2.edf will be first
    assert fnames[0].exists()
    return fnames


def to_pandas(edf_obj):
    """Convert an EDF file to a pandas DataFrame.

    Parameters
    ----------
    edf_obj : :class:`EDF`
        The EDF object to convert to a DataFrame.

    Returns
    -------
    df_samples : dict
        A dictionary of :class:`pandas.DataFrame`, containing the samples, blinks,
        saccades, fixations, messages, and calibrations.
    """
    pd = _check_pandas_installed(strict=True)

    dfs = {}
    dfs["discrete"] = {}

    # Discrete
    for key in edf_obj["discrete"]:
        cols = edf_obj["discrete"][key].dtype.names
        dfs["discrete"][key] = pd.DataFrame(edf_obj["discrete"][key], columns=cols)
        # XXX: pyeparse represented messages as byte strings. Should we change that?
        if key == "messages":
            dfs["discrete"][key]["msg"] = dfs["discrete"][key]["msg"].astype(str)
        elif key in ["blinks", "saccades", "fixations"]:
            dfs["discrete"][key]["eye"] = (dfs["discrete"][key]["eye"]).map(
                _defines.eye_constants
            )
    # Samples
    cols = edf_obj["info"]["sample_fields"]
    dfs["samples"] = pd.DataFrame(edf_obj["samples"].T, columns=cols)
    # Calibration
    if not edf_obj["info"]["calibrations"]:
        dfs["calibrations"] = pd.DataFrame()
        return dfs
    cals = [cal.copy() for cal in edf_obj["info"]["calibrations"]]
    validations = [cal.pop("validation") for cal in cals]
    val_dfs = []
    assert len(cals) == len(validations)
    for cal, validation in zip(cals, validations):
        this_df = pd.DataFrame(validation)
        this_df["eye"] = cal["eye"]
        this_df["model"] = cal["model"]
        this_df["onset"] = cal["onset"]
        val_dfs.append(this_df)
    dfs["calibrations"] = pd.concat(val_dfs)
    return dfs


def to_mne(edf_obj):
    """Create and Return an instance of MNE RawEyelink.

    Parameters
    ----------
    edf_obj : EDF
        The EDF object to convert to an MNE object.

    Returns
    -------
    raw : :class:`mne.io.Raw`
        The MNE RawEyelink instance.
    calibrations : list
        A list of Calibration objects.
    """
    mne = _check_mne_installed(strict=True)

    # in mne we need to specify the eye in the ch name, or pick functions will fail
    is_binocular = edf_obj["info"]["eye"] == "BINOCULAR"
    if is_binocular:
        ch_names = edf_obj["info"]["sample_fields"]
    else: # MONOCULAR
        eye = edf_obj["info"]["eye"].split("_")[0].lower()
        ch_names = edf_obj["info"]["sample_fields"]
        ch_names = [f"{ch}_{eye}" for ch in ch_names]
    ch_types = []
    more_info = {}
    # Set channel types
    for ch in ch_names:
        if is_binocular:
            eye = ch.split("_")[-1].lower()
            assert eye in ["left", "right"]
        if ch.startswith(("xpos", "ypos")):
            ch_types.append("eyegaze")
            if ch.startswith("x"):
                more_info[f"{ch}"] = ("eyegaze", "px", f"{eye}", "x")
            elif ch.startswith("y"):
                more_info[f"{ch}"] = ("eyegaze", "px", f"{eye}", "y")
        elif ch.startswith("ps"):
            ch_types.append("pupil")
            more_info[f"{ch}"] = ("pupil", "au", f"{eye}")
        else:
            warn(f"Unknown channel type: {ch}. Setting to misc.")
            ch_types.append("misc")

    # Create the info structure
    info = mne.create_info(
        ch_names=ch_names, sfreq=edf_obj["info"]["sfreq"], ch_types=ch_types
    )
    # force timezone to UTC
    dt = edf_obj["info"]["meas_date"]
    tz = timezone(timedelta(hours=0))
    dt = dt.replace(tzinfo=tz)
    info.set_meas_date(dt)

    # Create the raw object
    raw = mne.io.RawArray(edf_obj["samples"], info)
    # This will set the loc array etc.
    mne.preprocessing.eyetracking.set_channel_types_eyetrack(raw, more_info)
    # Add annotations
    raw = _add_annotations(edf_obj, raw)
    # Add calibration
    calibrations = _create_calibration(edf_obj)
    return raw, calibrations


def _add_annotations(edf, raw):
    """Add MNE Annotations of EyeLink Events to raw."""
    EYE_EVENTS = [
        ("blinks", "BAD_blink"),
        ("saccades", "saccade"),
        ("fixations", "fixation"),
    ]
    # blinks, saccades, fixations
    for ev, desc in EYE_EVENTS:
        onset = edf["discrete"][ev]["stime"]
        duration = edf["discrete"][ev]["etime"] - onset
        ch_names = [raw.info["ch_names"]] * len(onset)
        raw.annotations.append(onset, duration, desc, ch_names)
    # messages
    onset = edf["discrete"]["messages"]["stime"]
    duration = np.zeros_like(onset)
    desc = edf["discrete"]["messages"]["msg"].astype(str).squeeze()
    raw.annotations.append(onset, duration, desc)
    # TODO: buttons and inputs ?
    return raw


def _create_calibration(edf):
    """Create a calibration event."""
    from mne.preprocessing.eyetracking import Calibration

    calibrations = []
    for ii, this_cal in enumerate(edf["info"]["calibrations"]):
        eye = this_cal["eye"]
        x = this_cal["validation"]["point_x"]
        y = this_cal["validation"]["point_y"]
        positions = np.array([x, y]).T
        gx = x + this_cal["validation"]["diff_x"]
        gy = y + this_cal["validation"]["diff_y"]
        gaze = np.array([gx, gy]).T
        offsets = this_cal["validation"]["offset"]
        avg_error = np.round(np.mean(offsets), 3)
        max_error = np.max(offsets)
        screen_resolution = edf["info"]["screen_coords"]
        onset = this_cal["onset"]
        model = this_cal["model"]
        cal = Calibration(
            onset=onset,
            model=model,
            eye=eye,
            avg_error=avg_error,
            max_error=max_error,
            positions=positions,
            offsets=offsets,
            gaze=gaze,
            screen_resolution=screen_resolution,
        )
        calibrations.append(cal)
    return calibrations
