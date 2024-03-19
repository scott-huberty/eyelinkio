import pytest

from pyeyelink import read_raw
from pyeyelink.utils import _get_test_fnames, requires_edfapi

fnames = _get_test_fnames()

@requires_edfapi
def test_read_raw():
    """Test reading raw data."""
    for fname in fnames:
        read_raw(fname)
        break
    else:
        raise RuntimeError('No test files found')
    # XXX: add more tests
