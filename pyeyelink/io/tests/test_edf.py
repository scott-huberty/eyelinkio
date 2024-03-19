import numpy as np

from pyeyelink import read_raw
from pyeyelink.utils import _get_test_fnames, requires_edfapi

fnames = _get_test_fnames()

@requires_edfapi
def test_read_raw():
    """Test reading raw data."""
    for fname in fnames:
        raw = read_raw(fname)
        # test repr
        assert repr(raw)

        # tests dtypes are parsed correctly that is double only
        assert raw['samples'].dtype == np.float64

        if fname == 0:  # First test file has this property
            for kind in ['saccades', 'fixations', 'blinks']:
                assert raw["discrete"][kind][0]['stime'] < 12.0
        assert raw['times'][0] < 1.0
    # XXX: add more tests
