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
#  Date:   06/18/2009
#
#------------------------------------------------------------------------------

# Standard library imports
import codecs
from multiprocessing import Pool

# ETS imports
from enthought.traits.api import HasTraits, Int, Str, List, Bool, Any, \
    Property, on_trait_change
from enthought.traits.ui.extras.saving import CanSaveMixin

# Local imports. Because of an apparent bug in multiprocessing where functions
# cannot be defined outside the module where apply_async is called, we define
# some fake functions here.
import util
def docutils_rest_to_html(rest):
    return util.docutils_rest_to_html(rest)
def sphinx_rest_to_html(rest, static_path=util.DEFAULT_STATIC_PATH):
    return util.sphinx_rest_to_html(rest, static_path)


class DocUtilsWarning(HasTraits):
    level = Int
    line = Int
    description = Str


class ReSTHTMLPair(CanSaveMixin):
    rest = Str
    html = Str
    warnings = List(DocUtilsWarning)

    use_sphinx = Bool(False)
    sphinx_static_path = Str

    save_html = Bool(False)
    # The 'filepath' attribute of CanSaveMixin is for the ReST file
    html_filepath = Property(Str, depends_on='filepath')

    # Private traits
    _pool = Any
    _processing = Bool(False)
    _queued = Bool(False)

    #-----------------------------------------------------------------
    #  ReSTHTMLPair interface
    #-----------------------------------------------------------------

    def __init__(self, **kw):
        self._pool = Pool(processes=1)
        super(ReSTHTMLPair, self).__init__(**kw)
        if self.html == '' and not self._processing:
            self._processing = True
            self._gen_html()

    def _rest_changed(self):
        self.dirty = True

    @on_trait_change('rest, use_sphinx, sphinx_static_path')
    def _queue_html(self):
        if self._processing:
            self._queued = True
        else:
            self._processing = True
            self._gen_html()

    def _gen_html(self):
        args = [ self.rest ]
        if self.use_sphinx:
            func = sphinx_rest_to_html
            if self.sphinx_static_path:
                args.append(self.sphinx_static_path)
        else:
            func = docutils_rest_to_html
        #self._set_html(func(*args))
        self._pool.apply_async(func, args, callback=self._set_html)

    def _set_html(self, result):
        if self._queued:
            self._gen_html()
            self._queued = False
        else:
            self._processing = False
            self.html, warning_nodes = result
            warnings = []
            for node in warning_nodes:
                description = node.children[0].children[0]
                warnings.append(DocUtilsWarning(level=node.attributes['level'],
                                                line=node.attributes['line'],
                                                description=description))
            self.warnings = warnings

    def _get_html_filepath(self):
        filepath = self.filepath
        index = filepath.rfind('.')
        if index != -1:
            filepath = filepath[:index]
        return filepath + '.html'

    #-----------------------------------------------------------------
    #  CanSaveMixin interface
    #-----------------------------------------------------------------

    def validate(self):
        """ Prompt the user if there are warnings/errors with reST file.
        """
        if len(self.warnings):
            return (False, "The reStructured Text is improperly composed. " \
                           "Are you sure you want to save it?")
        else:
            return (True, '')

    def save(self):
        """ Save both the reST and HTML file.
        """
        self.dirty = False

        fh = codecs.open(self.filepath, 'w', 'utf-8')
        fh.write(self.rest)
        fh.close()

        if self.save_html:
            fh = codecs.open(self.html_filepath, 'w', 'utf-8')
            fh.write(self.html)
            fh.close()
