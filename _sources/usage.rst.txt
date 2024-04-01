.. _user-guide:

User Guide
==========

Installation
------------

This package is not yet available on PyPI, so you must install it from source. You can do
this by cloning the repository and running the following command in the root directory:

.. code:: bash

   pip install --editable .

This will install the package in "editable" mode, meaning that changes to the source code
will be reflected in the installed package. This is useful for development purposes.

Or you can install a static version of the package directly from GitHub:

.. code:: bash

   pip install git+https://github.com/scott-huberty/eyelinkio



Reading an EDF file
-------------------

You can read EyeLink EDF files using the :func:`~eyelinkio.io.edf.read_edf` function, which
returns an :class:`~eyelinkio.io.EDF` instance.

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


Converting to a DataFrame or MNE Raw instance
----------------------------------------------

You can convert an instance of EDF to a pandas DataFrame or an MNE Raw instance using the
``to_pandas`` and ``to_mne`` methods, respectively.

.. code:: python

   # Convert to a pandas DataFrame or an MNE Raw instance
   dfs = edf_file.to_pandas()
   raw, calibration = edf_file.to_mne()


.. seealso::

   `Working with eyetracking data in MNE <https://mne.tools/stable/auto_tutorials/preprocessing/90_eyetracking_data.html>`_