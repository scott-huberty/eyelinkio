=========
pyEyelink
=========

A lightweight library to import SR Research EDF files into Python.

**This Software is currenly pre-alpha, meaning it is currently being developed and is not ready for outside use**

About the Eyelink Data Format
=============================

The Eyelink Data Format (EDF; not to be confused with the `European Data Format <https://www.edfplus.info>`_ ) is used for storing eyetracking data from Eyelink eyetrackers. It was put forward by the company `SR Research <https://www.sr-research.com>`_. SR Research EDF files store data in a binary format, and reading these files currently requires the `edfapi` C library that is included in the Eyelink developers kit.

Dependencies
============

Strictly speaking, pyEyelink only requires Numpy, and that the user has the `Eyelink developers kit <https://www.sr-research.com/support/forum-3.html>`_ installed on their maching (One must create a login on the forum to access the download). We also plan to create helper functions for converting data to pandas `DataFrames` or MNE-Python Raw instances, after reading the data in. These functions would require the user to have those packages installed.


Acknowledgements
================

This package was originally adapted from the `pyeparse <https://github.com/pyeparse/pyeparse>`_ package (created by several of the core developers of `MNE-Python <https://mne.tools/dev/index.html>`_). It copies much of the EDF (Eyelink Data Format) reading code. 
