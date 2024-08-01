# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from datetime import date
from pathlib import Path

import eyelinkio

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
curpath = Path(__file__).parent.resolve(strict=True)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'EyeLinkIO'
author = 'EyeLinkIO Developers'
copyright = f"{date.today().year}, {author}"
release = eyelinkio.__version__
package = eyelinkio.__name__
gh_url = "https://github.com/scott-huberty/eyelinkio"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["numpydoc",
              "sphinx.ext.autodoc",
              "sphinx.ext.intersphinx",
              "sphinx.ext.todo",
              "sphinxemoji.sphinxemoji",
              # "sphinxcontrib.towncrier.ext",
              ]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', "changes/devel"]



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']

html_css_files = [
    'css/custom.css',
]

html_title = "EyeLinkIO 👀"

# -- Intersphinx configuration -----------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "mne": ("https://mne.tools/dev", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
}



# NumPyDoc configuration -----------------------------------------------------

numpydoc_class_members_toctree = False

numpydoc_show_inherited_class_members = False

numpydoc_attributes_as_param_list = True
numpydoc_xref_param_type = True

numpydoc_validate = True

numpydoc_xref_aliases = {
    # Python
    "file-like": ":term:`file-like <python:file object>`",
    "iterator": ":term:`iterator <python:iterator>`",
    "path-like": ":term:`path-like`",
    "array-like": ":term:`array_like <numpy:array_like>`",
    "Path": ":class:`python:pathlib.Path`",
    "bool": ":ref:`bool <python:typebool>`",
    # MNE
    "Raw": "mne.io.Raw",
    "RawEyelink": "mne.io.Raw",
    "Calibration": "mne.preprocessing.eyetracking.Calibration",
    # Pandas
    "DataFrame": "pandas.DataFrame",
    # eyelinkio
    "EDF": ":class:`~eyelinkio.io.EDF`",
}

numpydoc_xref_ignore = {"of", "A",}

# -- sphinxcontrib-towncrier configuration -----------------------------------

towncrier_draft_working_directory = str(curpath.parent)
