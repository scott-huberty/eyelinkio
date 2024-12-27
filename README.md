[![CircleCI](https://dl.circleci.com/status-badge/img/gh/scott-huberty/eyelinkio/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/scott-huberty/eyelinkio/tree/main)
[![PyPI version](https://badge.fury.io/py/eyelinkio.svg)](https://badge.fury.io/py/eyelinkio)
[![PyPI Download count](https://static.pepy.tech/badge/eyelinkio)](https://pepy.tech/project/eyelinkio)

# EyeLinkIO 👀

A lightweight library to import SR Research EDF files into Python.

**This Software is currenly pre-alpha, meaning it is currently being developed**: Changes to the API (function names, etc.) may occur without warning.

## About the Eyelink Data Format

The EyeLink Data Format (EDF; not to be confused with the
[European Data Format](<https://www.edfplus.info>)) is used for storing eyetracking data
from EyeLink eyetrackers. It was put forward by the company
[SR Research](<https://www.sr-research.com>). SR Research EDF files store data in a
binary format, and reading these files requires interfacing with ``eyelink-edfapi`` C
library that is typically included in the EyeLink Software Development Kit. EyeLinkIO
Includes the necessary binaries to read EDF files, but can also be configured to use the
EDF API library that is installed on your computer.

## Dependencies

Strictly speaking, EyeLinkIO only requires Numpy. For converting data to pandas ``DataFrames`` or MNE-Python ``Raw`` instances, you must have those respective packages installed.

> [!NOTE]
>
> - EyeLinkIO includes the Eyelink EDF API binary files that are needed to read EDF files.
> - [See](#using-the-eyelink-developers-kit-edf-api-to-read-edf-files) If you want to use the EyeLink Developers Kit's EDF API library that is installed on your computer.

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
> To use the editable installation, you should:
>
>- Fork the repository on GitHub first.
>- Clone your forked repository to your local machine.
>- Make sure you're in the directory *containing* the cloned `eyelinkio` folder when you run the command provided above

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

```console
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

```console
Out: dict_keys(['info', 'discrete', 'times', 'samples'])
```

```python

edf_file["info"].keys()
```

```console
Out: dict_keys(['meas_date', 'version', 'camera', 'serial', 'camera_config', 'sfreq', 'ps_units', 'eye', 'sample_fields', 'edfapi_version', 'screen_coords', 'calibrations', 'filename'])
```

```python

edf_file["discrete"].keys()
```

```console
Out: dict_keys(['messages', 'buttons', 'inputs', 'blinks', 'saccades', 'fixations'])
```

### Exporting an EDF object to Pandas or MNE-Python

```python
# Convert to a pandas DataFrame or an MNE Raw instance
dfs = edf_file.to_pandas()
raw, calibration = edf_file.to_mne()
```

See the [documentation](https://scott-huberty.github.io/eyelinkio/) for more.

#### Using The EyeLink Developers Kit (EDF API) to read EDF files

EyeLinkIO includes the Eyelink EDF API binary files that are needed to read EDF files,
and by default it will rely on these files when reading reading your EDF files. However,
if you have the
[Eyelink Developers Kit](https://www.sr-research.com/support/forum-9.html)
installed on your computer, you can explicitly direct
EyeLinkIO to rely on the EDF API library that is included in the EyeLink Developers Kit,
by setting the environment variable `EYELINKIO_USE_INSTALLED_EDFAPI` to `true` *before*
importing the package:

```python
import os
os.environ["EYELINKIO_USE_INSTALLED_EDFAPI"] = "true"

import eyelinkio
edf = eyelinkio.read_edf("path/to/edf/file")
```

> [!NOTE]
>
> - First download the [EyeLink Software Development Kit](<https://www.sr-research.com/support/forum-3.html>)
> - You must register an account on the forum to access the download (registration is free)

## Acknowledgements

This package was originally adapted from the [pyeparse](<https://github.com/pyeparse/pyeparse>) package (created by several of the core developers of [MNE-Python](<https://mne.tools/dev/index.html>)). It copies much of the EDF (Eyelink Data Format) reading code.

## Limitations

- Reading extra sample fields (velocity, HREF, head position etc.) from the EDF file is not yet supported.

See the [Roadmap](https://scott-huberty.github.io/eyelinkio/roadmap.html) for more details.
