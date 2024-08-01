.. _Scott Huberty: https://github.com/scott-huberty
.. _Thinh Nguyen: https://github.com/ttngu207

0.2.0 (2024-08-01) 📦
=====================

New features 🚀
---------------

- Added support for reading binocular data by `Scott Huberty`_ and `Thinh Nguyen`_. (`#5 <https://github.com/scott-huberty/eyelinkio/pulls/5>`__)

- Setup a changelog, using `towncrier <https://towncrier.readthedocs.io/en/stable/index.html>`_. by `Scott Huberty`_ (`#6 <https://github.com/scott-huberty/eyelinkio/pulls/6>`__)


Bugfixes 🐞
-----------

- Gracefully handle the case where an EDF file does not contain an expected event type (.e.g blinks, fixations, etc.) by `Thinh Nguyen`_. (`#7 <https://github.com/scott-huberty/eyelinkio/pull/7>`__)

API changes ⚠️
--------------

- The ``edf['info']['calibrations']`` key in an `EDF <file:///Users/scotterik/devel/repos/eyelinkio/docs/_build/html/API.html#edf-class>`_ object is no longer a single numpy array. It is now a dictionary, where the aforementioned array is stored under the sub-key ``"validation"``, .e.g ``my_edf['info']['calibrations']['validation']``.

.. _current:
