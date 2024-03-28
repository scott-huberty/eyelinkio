# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'EyeLinkIO'
copyright = '2024, EyeLinkIO Developers'
author = 'EyeLinkIO Developers'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["numpydoc",
              "sphinx.ext.autodoc",
              "sphinx.ext.intersphinx",
              "sphinx.ext.todo",
              "sphinxemoji.sphinxemoji",
              ]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



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
