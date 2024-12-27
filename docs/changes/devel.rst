.. _Scott Huberty: https://github.com/scott-huberty
.. _Thinh Nguyen: https://github.com/ttngu207
.. _Will Foran: https://github.com/WillForan


0.3 (2024-12-12) 📦
===================

Bugfixes 🐞
-----------

- Improved error message handling in the case that the EyeLink EDF API is not available. By `Will Foran`_ (`#11 <https://github.com/scott-huberty/eyelinkio/pull/11>`__)


New features 🚀
---------------

- You can now load EDF files without needing to install the EyeLink Developers Kit. By `Scott Huberty`_ (`#14 <https://github.com/scott-huberty/eyelinkio/pull/14>`__)
- Added Continuous Integration (CI) testing for Windows and MacOS. By `Scott Huberty`_  (`#14 <https://github.com/scott-huberty/eyelinkio/pull/14>`__)


0.2.0 (2024-08-01) 📦
=====================

New features 🚀
---------------

- Added support for reading binocular data by `Scott Huberty`_ and `Thinh Nguyen`_. (`#5 <https://github.com/scott-huberty/eyelinkio/pull/5>`__)

- Setup a changelog, using `towncrier <https://towncrier.readthedocs.io/en/stable/index.html>`_. by `Scott Huberty`_ (`#6 <https://github.com/scott-huberty/eyelinkio/pull/6>`__)


Bugfixes 🐞
-----------

- Gracefully handle the case where an EDF file does not contain an expected event type (.e.g blinks, fixations, etc.) by `Thinh Nguyen`_. (`#7 <https://github.com/scott-huberty/eyelinkio/pull/7>`__)

API changes ⚠️
--------------

- The ``edf['info']['calibrations']`` key in an `EDF <file:///Users/scotterik/devel/repos/eyelinkio/docs/_build/html/API.html#edf-class>`_ object is no longer a single numpy array. It is now a dictionary, where the aforementioned array is stored under the sub-key ``"validation"``, .e.g ``my_edf['info']['calibrations']['validation']``.

.. _current:
