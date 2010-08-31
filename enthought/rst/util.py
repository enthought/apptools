#------------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Evan Patterson
#  Date:   07/17/2009
#
#------------------------------------------------------------------------------

""" Defines function for converting reStructured Text to HTML.
"""

# Standard library imports
import codecs
import os.path
import re
from shutil import rmtree
from StringIO import StringIO
from tempfile import mkdtemp

# System library imports
import docutils.io, docutils.nodes
from docutils.core import Publisher
from docutils.parsers.rst.roles import _roles as docutils_roles
try:
    from sphinx.application import Sphinx
except ImportError:
    Sphinx = None
try:
    from rst2pdf.createpdf import main as rst2pdf
except ImportError:
    rst2pdf = None


#------------------------------------------------------------------------------
# Convert reStructured Text to various formats using docutils
#------------------------------------------------------------------------------

def docutils_rest_to_html(rest):
    """ Uses docutils to convert a ReST string to HTML. Returns a tuple
        containg the HTML string and the list of warning nodes that were
        removed from the HTML.
    """
    return _docutils_rest_to(rest, 'html')

def docutils_rest_to_latex(rest):
    """ Uses docutils to convert a ReST string to LaTeX. Returns a tuple
        containg the LaTeX string and the list of warning nodes.
    """
    return _docutils_rest_to(rest, 'latex')

def _docutils_rest_to(rest, writer):
    """ Uses docutils to convert a ReST string to HTML. Returns a tuple
        containg the HTML string and the list of warning nodes that were
        removed from the HTML.
    """
    # Make sure any Sphinx polution of docutils has been removed.
    if Sphinx is not None:
        for key, value in docutils_roles.items():
            if value.__module__.startswith('sphinx'):
                docutils_roles.pop(key)

    pub = Publisher(source_class=docutils.io.StringInput,
                    destination_class=docutils.io.StringOutput)
    pub.set_reader('standalone', None, 'restructuredtext')
    pub.set_writer(writer)
    pub.writer.default_stylesheet_path=''
    pub.get_settings() # Get the default settings
    pub.settings.halt_level = 6 # Don't halt on errors
    pub.settings.warning_stream = StringIO()

    pub.set_source(rest)
    pub.set_destination()
    pub.document = pub.reader.read(pub.source, pub.parser, pub.settings)
    pub.apply_transforms()

    # Walk the node structure of a docutils document and remove 'problematic'
    # and 'system_message' nodes. Save the system_message nodes.
    warning_nodes = []
    for node in pub.document.traverse(docutils.nodes.problematic):
        node.parent.replace(node, node.children[0])
    for node in pub.document.traverse(docutils.nodes.system_message):
        warning_nodes.append(node)
        node.parent.remove(node)

    return pub.writer.write(pub.document, pub.destination), warning_nodes


#------------------------------------------------------------------------------
# Convert reStructured Text to HTML using Sphinx
#------------------------------------------------------------------------------

DEFAULT_STATIC_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   'sphinx_default')

STATIC_REGEX = re.compile(r'(src|href)=["\']_static([\s\w/\.]+?)["\']',
                          re.IGNORECASE)

if Sphinx is not None:
    # Ugly hack. The Sphinx source code suggests that None should be a valid
    # value for confdir. On Windows, however, os.path falls over if it gets a
    # None value. This hack ensures that sphinx.config.Config.__init__ gets
    # passed a valid string for the config directory.
    import sphinx.builders.html
    def my_init(self, app):
        app.confdir = ''
        sphinx.builders.Builder.__init__(self, app)
        app.confdir = None
    sphinx.builders.html.StandaloneHTMLBuilder.__init__ = my_init

    # Effectively remove the 'finish' function of the Sphinx HTML Builder. This
    # saves a lot of file copying that we don't care about.
    def my_finish(self):
        return
    sphinx.builders.html.StandaloneHTMLBuilder.finish = my_finish

def sphinx_rest_to_html(rest, static_path=DEFAULT_STATIC_PATH):
    """ Uses sphinx to convert a ReST string to HTML. Requires the use of
        temporary files. Returns the same things as docutils_rest_to_html.
    """

    # Hijack the warning filter method in Sphinx so that we can save the nodes
    # that were removed.
    warning_nodes = []
    def my_filter_messages(self, doctree):
        for node in doctree.traverse(docutils.nodes.system_message):
            warning_nodes.append(node)
            node.parent.remove(node)
    import sphinx.environment
    sphinx.environment.BuildEnvironment.filter_messages = my_filter_messages

    temp_dir = mkdtemp(prefix='rest-editor-')
    try:
        filename = 'sphinx_preview'
        base_path = os.path.join(temp_dir, filename)
        fh = codecs.open(base_path+'.rst', 'w', 'utf-8')
        fh.write(rest)
        fh.close()

        overrides = { 'html_add_permalinks' : False,
                      'html_copy_source' : False,
                      'html_title' : 'Sphinx preview',
                      'html_use_index' : False,
                      'html_use_modindex' : False,
                      'html_use_smartypants' : True,
                      'master_doc' : filename }
        app = Sphinx(srcdir=temp_dir, confdir=None, outdir=temp_dir,
                     doctreedir=temp_dir, buildername='html',
                     confoverrides=overrides, status=None, warning=StringIO())
        app.build(force_all=True, filenames=None)

        fh = codecs.open(base_path+'.html', 'r', 'utf-8')
        html = fh.read()
        fh.close()
    finally:
        rmtree(temp_dir)

    # Replace the "_static/..." references inserted by Sphinx with absolute
    # links to the specified static_path replacement.
    def replace(m):
        return '%s="file://%s%s"' % (m.group(1), static_path, m.group(2))
    html = re.sub(STATIC_REGEX, replace, html)

    return html, warning_nodes

#------------------------------------------------------------------------------
# Convert reStructured Text to PDF using rst2pdf
#------------------------------------------------------------------------------

def rest_to_pdf(input_file, output_file):
    if rst2pdf is None:
        print 'rst2pdf package not installed.'
        return

    # rst2pdf doesn't seem to have an easy API so instead we call the main
    # function as if we were using it from the CLI

    args=['',input_file, '-o', output_file]
    rst2pdf(args[1:])