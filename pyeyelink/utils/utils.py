from pathlib import Path

from ..io.edf import _defines
from .check import _check_pandas_installed


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
        df["eye"] = (df["eye"] + 1).map(_defines.eye_constants)
        # TODO: from pyeparse, both eye and eye_idx are ints, but eye_idx is used
        #       as the int representation of the eye (-1, 0, 1), where eye is (0, 1, 2).
        #       This is strange bc eye would actually be the index (0-based)? This
        #       introduces potential for confusion, but I'm going to leave it as is for
        #       now, and this is why I'm adding 1 to the eye column above.
    return df
