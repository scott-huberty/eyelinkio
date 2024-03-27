Contributor Guide
=================

This package is actively seeking contributors! If you are interested in contributing
to this package, please read the following guide.

Install the development dependencies
--------------------------------------

Assuming you have forked EyeLinkIO, and cloned your fork to your local machine, you can
install the development dependencies by running the following command from the root of
the package:

.. code-block:: bash

    $ pip install -e '.[dev]'


Running the tests
-----------------

We use `pytest <https://docs.pytest.org/en/latest/>`_ to run unit tests,
`ruff <https://astral.sh/ruff>`_ to run linting, and
`NumpyDoc <https://numpydoc.readthedocs.io/en/latest/>`_ to check and build docstrings.
To run the tests after you have installed the development dependencies, run the
following command from the root of the package:

.. code-block:: bash

    $ pytest

.. code-block:: bash

    $ ruff check eyelinkio

To build the docs:

.. code-block:: bash

    $ cd docs
    $ make html

