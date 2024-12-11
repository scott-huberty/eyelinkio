# Authors: Scott Huberty <seh33@uw.edu>
# Aknowledgements to the devs of the pyeparse package, from which this is derived
#
# License: BSD (3-clause)

from . import utils

from .edf import read_edf, EDF

try:
    from importlib.metadata import version

    __version__ = version("eyelinkio")
except Exception:
    __version__ = "0.0.0"