# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'uC chip interface'
copyright = '2023, Ole Richter'
author = 'Ole Richter'
release = '0.9.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
   'sphinx.ext.autosummary',]

templates_path = ['_templates']
exclude_patterns = []

autosummary_imported_members=True



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

import sys
import os
sys.path.insert(0, os.path.abspath("../.."))
sys.path.append("../")