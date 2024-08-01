# EyeLinkIO 👀

A lightweight library to import SR Research EDF files into Python.

**This Software is currenly pre-alpha, meaning it is currently being developed**: Changes to the API (function names, etc.) may occur without warning. This library has been tested with MacOS and Linux, but not Windows.

## About the Eyelink Data Format

The EyeLink Data Format (EDF; not to be confused with the [European Data Format](<https://www.edfplus.info>)) is used for storing eyetracking data from EyeLink eyetrackers. It was put forward by the company [SR Research](<https://www.sr-research.com>). SR Research EDF files store data in a binary format, and reading these files currently requires the ``eyelink-edfapi`` C library that is included in the EyeLink Software Development Kit.

## Dependencies

Strictly speaking, EyeLinkIO only requires Numpy. For converting data to pandas ``DataFrames`` or MNE-Python ``Raw`` instances, you must have those respective packages installed.

> [!IMPORTANT]
> - You must have the [EyeLink Software Development Kit](<https://www.sr-research.com/support/forum-3.html>) installed on your computer
> - You must register an account on the forum to access the download (registration is free)

## Installation

1. **Stable Installation**

```bash

pip install eyelinkio
```

2. **Development Installation** (For those who need features or bugfixes that aren't released yet):

```bash

pip install git+https://github.com/scott-huberty/eyelinkio.git
```
3. **Editable Installation** (For contributors to EyeLinkIO):

```bash

pip install -e ./eyelinkio
```

> [!IMPORTANT]  
>- Fork the repository on GitHub first.
>- Clone your forked repository to your local machine.
>- Make sure you're in the directory *containing* the cloned `eyelinkio` folder when you run the command above

This package is not currently available on Conda.

## Example Usage

#### Reading an EDF file

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

#### Inspecting an EDF object

```python

edf_file.keys()
```

```bash
Out: dict_keys(['info', 'discrete', 'times', 'samples'])
```

```python

edf_file["info"].keys()
```

```bash
Out: dict_keys(['meas_date', 'version', 'camera', 'serial', 'camera_config', 'sfreq', 'ps_units', 'eye', 'sample_fields', 'edfapi_version', 'screen_coords', 'calibrations', 'filename'])
```

```python

edf_file["discrete"].keys()
```

```bash
Out: dict_keys(['messages', 'buttons', 'inputs', 'blinks', 'saccades', 'fixations'])
```

### Exporting an EDF object to Pandas or MNE-Python

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
