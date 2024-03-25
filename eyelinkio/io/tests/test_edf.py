import numpy as np
import pytest

from eyelinkio.io import read_edf
from eyelinkio.utils.check import requires_edfapi
from eyelinkio.utils.utils import _get_test_fnames

fnames = _get_test_fnames()

@requires_edfapi
def test_read_raw():
    """Test reading raw data."""
    for fname in fnames:
        edf_file = read_edf(fname)
        # test repr
        assert repr(edf_file)

        # tests dtypes are parsed correctly that is double only
        assert edf_file['samples'].dtype == np.float64

        if fname == 0:  # First test file has this property
            for kind in ['saccades', 'fixations', 'blinks']:
                assert edf_file["discrete"][kind][0]['stime'] < 12.0
        assert edf_file['times'][0] < 1.0
        assert edf_file["info"]["eye"] == "LEFT_EYE"
        assert edf_file["info"]["ps_units"] == "PUPIL_AREA"

pytest.importorskip('pandas')
def test_to_data_frame():
    """Test converting EDF to pandas DataFrame."""
    import pandas as pd

    fname = _get_test_fnames()[0]
    edf_file = read_edf(fname)
    dfs = edf_file.to_data_frame()
    assert isinstance(dfs, dict)
    assert all(isinstance(df, pd.DataFrame) for df in dfs.values())
    np.testing.assert_equal(dfs["blinks"]["eye"].unique(), "LEFT_EYE")
    assert dfs["messages"]["msg"][0] == "RECCFG CR 1000 2 1 L"
