# -*- coding: utf-8 -*-
# Authors: Denis Engemann <denis.engemann@gmail.com>
#
# License: BSD (3-clause)

##############################################################################
# Py2/3

import numpy as np
import warnings

# Iterator
try:
    advance_iterator = next
except NameError:
    def advance_iterator(it):
        return it.next()
next = advance_iterator

# Basestring
try:
    string_types = basestring  # noqa
except NameError:
    string_types = str

# StringIO
try:
    from cStringIO import StringIO
except ImportError:  # py3 has renamed this
    from io import StringIO  # noqa
from io import BytesIO  # noqa

# -*- coding: utf-8 -*-


##############################################################################
# numpy backports
def _replace_nan(a, val):
    is_new = not isinstance(a, np.ndarray)
    if is_new:
        a = np.array(a)
    if not issubclass(a.dtype.type, np.inexact):
        return a, None
    if not is_new:
        # need copy
        a = np.array(a, subok=True)

    mask = np.isnan(a)
    np.copyto(a, val, where=mask)
    return a, mask


def _copyto(a, val, mask):
    if isinstance(a, np.ndarray):
        np.copyto(a, val, where=mask, casting='unsafe')
    else:
        a = a.dtype.type(val)
    return a


def _divide_by_count(a, b, out=None):
    with np.errstate(invalid='ignore'):
        if isinstance(a, np.ndarray):
            if out is None:
                return np.divide(a, b, out=a, casting='unsafe')
            else:
                return np.divide(a, b, out=out, casting='unsafe')
        else:
            if out is None:
                return a.dtype.type(a / b)
            else:
                # This is questionable, but currently a numpy scalar can
                # be output to a zero dimensional array.
                return np.divide(a, b, out=out, casting='unsafe')


def nanmean(a, axis=None, dtype=None, out=None, keepdims=False):
    arr, mask = _replace_nan(a, 0)
    if mask is None:
        return np.mean(arr, axis=axis, dtype=dtype, out=out, keepdims=keepdims)

    if dtype is not None:
        dtype = np.dtype(dtype)
    if dtype is not None and not issubclass(dtype.type, np.inexact):
        raise TypeError("If a is inexact, then dtype must be inexact")
    if out is not None and not issubclass(out.dtype.type, np.inexact):
        raise TypeError("If a is inexact, then out must be inexact")

    # The warning context speeds things up.
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        cnt = np.sum(~mask, axis=axis, dtype=np.intp, keepdims=keepdims)
        tot = np.sum(arr, axis=axis, dtype=dtype, out=out, keepdims=keepdims)
        avg = _divide_by_count(tot, cnt, out=out)

    isbad = (cnt == 0)
    if isbad.any():
        warnings.warn("Mean of empty slice", RuntimeWarning)
        # NaN is the only possible bad value, so no further
        # action is needed to handle bad results.
    return avg


def nanvar(a, axis=None, dtype=None, out=None, ddof=0, keepdims=False):
    arr, mask = _replace_nan(a, 0)
    if mask is None:
        return np.var(arr, axis=axis, dtype=dtype, out=out, ddof=ddof,
                      keepdims=keepdims)

    if dtype is not None:
        dtype = np.dtype(dtype)
    if dtype is not None and not issubclass(dtype.type, np.inexact):
        raise TypeError("If a is inexact, then dtype must be inexact")
    if out is not None and not issubclass(out.dtype.type, np.inexact):
        raise TypeError("If a is inexact, then out must be inexact")

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')

        # Compute mean
        cnt = np.sum(~mask, axis=axis, dtype=np.intp, keepdims=True)
        avg = np.sum(arr, axis=axis, dtype=dtype, keepdims=True)
        avg = _divide_by_count(avg, cnt)

        # Compute squared deviation from mean.
        arr -= avg
        arr = _copyto(arr, 0, mask)
        if issubclass(arr.dtype.type, np.complexfloating):
            sqr = np.multiply(arr, arr.conj(), out=arr).real
        else:
            sqr = np.multiply(arr, arr, out=arr)

        # Compute variance.
        var = np.sum(sqr, axis=axis, dtype=dtype, out=out, keepdims=keepdims)
        if var.ndim < cnt.ndim:
            # Subclasses of ndarray may ignore keepdims, so check here.
            cnt = cnt.squeeze(axis)
        dof = cnt - ddof
        var = _divide_by_count(var, dof)

    isbad = (dof <= 0)
    if np.any(isbad):
        warnings.warn("Degrees of freedom <= 0 for slice.", RuntimeWarning)
        # NaN, inf, or negative numbers are all possible bad
        # values, so explicitly replace them with NaN.
        var = _copyto(var, np.nan, isbad)
    return var


def nanstd(a, axis=None, dtype=None, out=None, ddof=0, keepdims=False):
    var = nanvar(a, axis=axis, dtype=dtype, out=out, ddof=ddof,
                 keepdims=keepdims)
    if isinstance(var, np.ndarray):
        std = np.sqrt(var, out=var)
    else:
        std = var.dtype.type(np.sqrt(var))
    return std
