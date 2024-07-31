# EyeLinkIO

A lightweight library to import SR Research EDF files into Python.

**This Software is currenly pre-alpha, meaning it is currently being developed**: Changes to the API (function names, etc.) may occur without warning. This library has been tested with MacOS and Linux, but not Windows.

## About the Eyelink Data Format

The EyeLink Data Format (EDF; not to be confused with the [European Data Format](<https://www.edfplus.info>)) is used for storing eyetracking data from EyeLink eyetrackers. It was put forward by the company [SR Research](<https://www.sr-research.com>). SR Research EDF files store data in a binary format, and reading these files currently requires the ``eyelink-edfapi`` C library that is included in the EyeLink Software Development Kit.

## Dependencies

Strictly speaking, EyeLinkIO only requires Numpy, and that the user has the [EyeLink Software Development Kit](<https://www.sr-research.com/support/forum-3.html>) installed on their machine (One must create a login on the forum to access the download). For converting data to pandas ``DataFrames`` or MNE-Python ``Raw`` instances, you must have those respective packages installed.

## Example Usage

```python

from eyelinkio import read_edf
eyelinkio.utils import _get_test_fnames  # for demonstration purposes only

fname = _get_test_fnames()[0]  # Replace this function with the path to your EDF file
edf_file = read_edf(fname)
print(edf_file)
```

```bash
<EDF | test_raw.edf> 
  Version: EYELINK II 1 
  Eye: LEFT_EYE 
  Pupil unit: PUPIL_AREA 
  Sampling frequency: 1000.0 Hz 
  Calibrations: 1 
  Length: 66.827 seconds 
```

```python
# Convert to a pandas DataFrame or an MNE Raw instance
dfs = edf_file.to_pandas()
raw, calibration = edf_file.to_mne()
```

See the [documentation](https://scott-huberty.github.io/eyelinkio/) for more.

## Acknowledgements

This package was originally adapted from the [pyeparse](<https://github.com/pyeparse/pyeparse>) package (created by several of the core developers of [MNE-Python](<https://mne.tools/dev/index.html>)). It copies much of the EDF (Eyelink Data Format) reading code.

## Limitations

- Reading extra sample fields (velocity, HREF, head position etc.) from the EDF file is not yet supported.

See the [Roadmap](https://scott-huberty.github.io/eyelinkio/roadmap.html) for more details.
