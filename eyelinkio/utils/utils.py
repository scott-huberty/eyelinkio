from datetime import timedelta, timezone
from pathlib import Path
from warnings import warn

from ..io.edf import _defines
from .check import _check_mne_installed, _check_pandas_installed


def _get_test_fnames():
    """Get usable test files (omit EDF if no edf2asc)."""
    path = Path(__file__).parent.parent / 'io' / 'tests' / 'data'
    fnames = list(path.glob('*.edf'))
    assert fnames[0].exists()
    return fnames

def to_data_frame(edf_obj):
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

    # Samples
    cols = edf_obj["info"]["sample_fields"]
    dfs["samples"] = pd.DataFrame(edf_obj["samples"].T, columns=cols)
    # Ocular events
    dfs["blinks"] = _convert_discrete_data(edf_obj["discrete"]["blinks"], "blinks")
    dfs["saccades"] = _convert_discrete_data(edf_obj["discrete"]["saccades"],
                                             "saccades")
    dfs["fixations"] = _convert_discrete_data(edf_obj["discrete"]["fixations"],
                                              "fixations")
    dfs["messages"] = _convert_discrete_data(edf_obj["discrete"]["messages"],
                                             "messages")
    # Calibration
    dfs["calibrations"] = pd.DataFrame(edf_obj["info"]["calibrations"].squeeze(),
                                       columns=edf_obj["info"]["calibrations"].dtype.names)

    return dfs


def _convert_discrete_data(data, field_name):
    import pandas as pd

    df = pd.DataFrame(data)
    if field_name == "messages":
        df["msg"] = df["msg"].str.decode("utf-8")
        # TODO: pyeparse represented messages as byte strings.
        #       Maybe we should use unicode strings
    else:
        df["eye"] = (df["eye"]).map(_defines.eye_constants)
    return df


def to_mne(edf_obj):
    """Convert an EDF object to an MNE object.

    Parameters
    ----------
    edf_obj : :class:`EDF`
        The EDF object to convert to an MNE object.

    Returns
    -------
    raw : :class:`mne.io.Raw
    """
    mne = _check_mne_installed(strict=True)

    # in mne we need to specify the eye in the ch name, or pick functions will fail
    eye = edf_obj["info"]["eye"].split("_")[0].lower()
    ch_names = edf_obj["info"]["sample_fields"]
    ch_names = [f"{ch}_{eye}" for ch in ch_names]
    ch_types = []
    more_info = {}
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
    info = mne.create_info(ch_names=ch_names,
                       sfreq=edf_obj["info"]["sfreq"],
                       ch_types=ch_types)
    # force timezone to UTC
    dt = edf_obj["info"]["meas_date"]
    tz = timezone(timedelta(hours=0))
    dt = dt.replace(tzinfo=tz)
    info.set_meas_date(dt)

    # Create the raw object
    raw = mne.io.RawArray(edf_obj["samples"], info)
    # This will set the loc array etc.
    mne.preprocessing.eyetracking.set_channel_types_eyetrack(raw, more_info)
    return raw
