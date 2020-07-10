# Configuration file for the Sphinx documentation builder.
import subprocess
import time

with open('Doxyfile.in') as f:
    txt = f.read()

txt = txt.replace('@DOXYGEN_OUTPUT_DIR@', 'build_doxygen/doxygen')
txt = txt.replace('@DOXYGEN_INPUT_DIRS@', '..')
with open('_Doxyfile', 'w') as f:
    f.write(txt)
time.sleep(0.1)
subprocess.call("mkdir -p build_doxygen; doxygen _Doxyfile", shell=True)

# -- Project information -----------------------------------------------------

project = "Smoldyn"
copyright = "2020, Steven S. Andrews"
author = "Steven S. Andrews"

# The full version, including alpha/beta/rc tags
release = "2.63.dev"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.imgmath",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinxcontrib.programoutput",
    "sphinx.ext.todo",
    "sphinx_rtd_theme",
    "recommonmark",
    "breathe",
    "sphinx_autodoc_typehints",
    "sphinx.ext.autosummary",
]

autoclass_content = "both"

autodoc_default_options = {
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "show_inheritance": True,
}

breathe_default_project = "smoldyn"

# generated by doxygen.
html_extra_path = ["build_doxygen"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

source_parsers = {
    ".md": "recommonmark.parser.CommonMarkParser",
}
source_suffix = [".rst", ".md"]