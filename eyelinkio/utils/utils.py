from datetime import timedelta, timezone
from pathlib import Path
from warnings import warn

import numpy as np

from ..io.edf import _defines
from .check import _check_mne_installed, _check_pandas_installed


def _get_test_fnames():
    """Get usable test files (omit EDF if no edf2asc)."""
    path = Path(__file__).parent.parent / "io" / "tests" / "data"
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
    dfs["calibrations"] = pd.DataFrame(
        edf_obj["info"]["calibrations"].squeeze(),
        columns=edf_obj["info"]["calibrations"].dtype.names,
    )
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
    eye = edf_obj["info"]["eye"].split("_")[0].lower()
    ch_names = edf_obj["info"]["sample_fields"]
    ch_names = [f"{ch}_{eye}" for ch in ch_names]
    ch_types = []
    more_info = {}
    # Set channel types
    for ch in ch_names:
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
        eye = edf["info"]["eye"].split("_")[0].lower()
        x = this_cal["point_x"]
        y = this_cal["point_y"]
        positions = np.array([x, y]).T
        gx = x + this_cal["diff_x"]
        gy = y + this_cal["diff_y"]
        gaze = np.array([gx, gy]).T
        offsets = this_cal["offset"]
        avg_error = np.mean(this_cal["offset"])
        max_error = np.max(this_cal["offset"])
        screen_resolution = edf["info"]["screen_coords"]
        # XXX: getting onset and model will be tricky.
        # XXX: for binocular data, we will need to get the eye another way
        cal = Calibration(
            onset=None,
            model=None,
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
