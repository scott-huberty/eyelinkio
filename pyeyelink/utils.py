import glob
import os.path as op

import numpy as np


def _get_test_fnames():
    """Get usable test files (omit EDF if no edf2asc)."""
    path = op.join(op.dirname(__file__), 'io', 'tests', 'data')
    fnames = glob.glob(op.join(path, '*.edf'))
    return fnames


def _has_edfapi():
    """Determine if a user has edfapi installed."""
    from .io.edf._raw import has_edfapi
    return has_edfapi


def _check_edfapi():
    """Check if edfapi is installed."""
    if not _has_edfapi():
        raise RuntimeError('edfapi is not installed')


def requires_edfapi(func):
    """Skip testing if edfapi is not installed."""
    import pytest
    return pytest.mark.skipif(not _has_edfapi(), reason='Requires edfapi')(func)