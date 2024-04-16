EyeLinkIO
=========

A lightweight library to import SR Research EDF files into Python.

.. important::
   **This Software is pre-alpha, meaning it is currently being developed**: Changes to the
   API (function names, etc.) may occur without warning. This library has been tested with
   MacOS and Linux, but not Windows.

About the EyeLink Data Format
=============================

The EyeLink Data Format (EDF; not to be confused with the
`European Data Format <https://www.edfplus.info>`_) is used for storing eyetracking data
from EyeLink eyetrackers. It was put forward by the company
`SR Research <https://www.sr-research.com>`_. SR Research EDF files store data in a
binary format, and reading these files currently requires the `eyelink-edfapi` C
library that is included in the Eyelink Software Developers Kit.

Dependencies
============

Strictly speaking, EyeLinkIO only requires Numpy, and that the user has the
`EyeLink Software Developers Kit <https://www.sr-research.com/support/forum-3.html>`_
installed on their machine (One must create a login on the forum to access the download).
We also provide helper functions for converting data to pandas `DataFrames` or MNE-Python
`Raw` instances, after reading the data in. These functions require the user to have those
respective packages installed.


Example Usage
=============

See the :ref:`user-guide`.


Acknowledgements
================

This package was originally adapted from the `pyeparse <https://github.com/pyeparse/pyeparse>`_
package (created by several of the core developers of `MNE-Python <https://mne.tools/dev/index.html>`_).
It copies much of the EDF (EyeLink Data Format) reading code. 


.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   usage
   contributing
   API
   roadmap
   whats_new