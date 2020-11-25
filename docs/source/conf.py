# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# -*- coding: utf-8 -*-
#
# EnvisageCore documentation build configuration file, created by
# sphinx-quickstart on Fri Jul 18 17:09:28 2008.
#
# This file is execfile()d with the current directory set to its containing dir
#
# The contents of this file are pickled, so don't put values in the namespace
# that aren't pickleable (module imports are okay, they're removed
# automatically).
#
# All configuration values have a default value; values that are commented out
# serve to show the default value.

import apptools
import enthought_sphinx_theme

# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'traits.util.trait_documenter',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General substitutions.
project = 'apptools'
copyright = '2008-2020, Enthought'

# The default replacements for |version| and |release|, also used in various
# other places throughout the built documents.
version = release = apptools.__version__

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = '%B %d, %Y'

# Options for autodoc
# -------------------

# Apptools offers an envisage plugin that requires importing from
# envisage.
try:
    import envisage  # noqa
except ImportError:
    autodoc_mock_imports = [
        'envisage',
    ]

# Options for HTML output
# -----------------------

# Use the Enthought Sphinx Theme (see
# https://github.com/enthought/enthought-sphinx-theme)
html_theme_path = [enthought_sphinx_theme.theme_path]
html_theme = "enthought"

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = "Apptools Documentation"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = "%b %d, %Y"

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
html_use_smartypants = True

# If false, no module index is generated.
html_use_modindex = False

# Output file base name for HTML help builder.
htmlhelp_basename = 'AppToolsdoc'


# Options for LaTeX output
# ------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class
# [howto/manual]).
latex_documents = [
    (
        'index',
        'AppTools.tex',
        'AppTools Documentation',
        'Enthought, Inc.',
        'manual'
    ),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
latex_logo = "e-logo-rev.png"
