.. _user-guide:

User Guide
==========

Installation
------------

.. note::
   This package is not yet available on conda-forge.

1. Stable Installation
~~~~~~~~~~~~~~~~~~~~~~~

You can install the latest stable version of the package from PyPI using pip:

.. code:: bash

   pip install eyelinkio


2. **Development Installation** (Static)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For those who need features or bugfixes that aren't released yet:

.. code:: bash

   pip install git+https://github.com/scott-huberty/eyelinkio


3. **Development Installation** (Dynamic)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For contributors to EyeLinkIO:

.. code:: bash

   pip install --editable ./eyelinkio

.. important::

   To install the package in editable mode, you must:

   - Fork the repository on GitHub first.
   - Clone your forked repository to your computer.
   - Make sure you're in the directory *containing* the cloned ``eyelinkio`` folder when you run the command provided above.

Example Usage
-------------

Reading an EDF file
~~~~~~~~~~~~~~~~~~~

You can read EyeLink EDF files using the :func:`~eyelinkio.edf.read_edf` function, which
returns an :class:`~eyelinkio.EDF` instance.

.. code:: python

   from eyelinkio.io import read_edf
   eyelinkio.utils import _get_test_fnames  # for demonstration purposes only

   fname = _get_test_fnames()[0]  # Replace this function with the path to your EDF file
   edf_file = read_edf(fname)
   print(edf_file)

.. code:: console

   <EDF | test_raw.edf> 
   Version: EYELINK II 1 
   Eye: LEFT_EYE 
   Pupil unit: PUPIL_AREA 
   Sampling frequency: 1000.0 Hz 
   Calibrations: 1 
   Length: 66.827 seconds 

Inspecting an EDF object
~~~~~~~~~~~~~~~~~~~~~~~~~

An EDF object inherits from a dictionary, so you can index it like a dictionary, and inspect its keys.

.. code:: python

   # Inspect the EDF object
   edf_file.keys()


.. code:: console
   
      dict_keys(['info', 'discrete', 'times', 'samples'])


.. code:: python

   # Inspect the info
   edf_file['info'].keys()


.. code:: console

   dict_keys(['meas_date', 'version', 'camera', 'serial', 'camera_config', 'sfreq', 'ps_units', 'eye', 'sample_fields', 'edfapi_version', 'screen_coords', 'calibrations', 'filename'])

.. code:: python

   # Inspect the events
   edf_file["discrete"].keys()

.. code:: console

   dict_keys(['messages', 'buttons', 'inputs', 'blinks', 'saccades', 'fixations'])

.. code:: python


   # Inspect the calibrations
   edf_file['info']['calibrations']


Converting to a DataFrame or MNE Raw instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can convert an instance of EDF to a pandas DataFrame or an MNE Raw instance using the
:meth:`~eyelinkio.EDF.to_pandas` and :meth:`~eyelinkio.EDF.to_mne` methods, respectively.

.. code:: python

   # Convert to a pandas DataFrame or an MNE Raw instance
   dfs = edf_file.to_pandas()
   raw, calibrations = edf_file.to_mne()


.. seealso::

   `Working with eyetracking data in MNE <https://mne.tools/stable/auto_tutorials/preprocessing/90_eyetracking_data.html>`_


Using the EDF API Library installed on your system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have the EDF API Library installed on your system, you can explicitly direct
EyeLinkIO to rely on it when reading your EDF files. This can be done by setting the
``EYELINKIO_USE_INSTALLED_EDFAPI`` parameter to ``true`` before importing EyeLinkIO.

.. code:: python

   import os
   os.environ["EYELINKIO_USE_INSTALLED_EDFAPI"] = "true"

   from eyelinkio.io import read_edf

   fname = _get_test_fnames()[0]  # Replace this function with the path to your EDF file
   edf_file = read_edf(fname)
   print(edf_file)

Otherwise, EyeLinkIO will rely on the EDF API Library that comes with the package.

.. note::

   If you want to install the EyeLink Developers Kit, you can download it from the
   `SR Research website <https://www.sr-research.com/support/forum-3.html>`_. You will
   need to register an account to access the download page (registration is free).