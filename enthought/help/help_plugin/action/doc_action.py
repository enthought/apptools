""" (Pyface) Action for displaying a help doc. 

    :Copyright: 2008, Enthought Inc.
    :License: BSD
    :Author: Janet Swisher    
"""
# This software is provided without warranty under the terms of the BSD
# license included in AppTools/trunk/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!


# Standard library imports.
import logging
from os.path import isabs, join, normpath
from subprocess import Popen
import sys 

# Enthought library imports.
from enthought.envisage.api import IExtensionPointUser, IExtensionRegistry
from enthought.pyface.workbench.action.workbench_action import WorkbenchAction
from enthought.traits.api import Instance, implements, Property

from enthought.help.help_plugin.api import HelpDoc

# Local imports
from util import get_sys_prefix_relative_filename

# Logging.
logger = logging.getLogger(__name__)

# This module's parent package.
PARENT = '.'.join(__name__.split('.')[:-2])

class DocAction(WorkbenchAction):
    """ (Pyface) Action for displaying a help doc.
    """
    implements(IExtensionPointUser)
    
    ### IExtensionPointUser interface
    extension_registry = Property(Instance(IExtensionRegistry))
    
    def _get_extension_registry(self):
        return self.window.application.extension_registry
    
    ### HelpDocAction interface
    
    # Help doc associated with this action.
    my_help_doc = Instance(HelpDoc)
    
    def _my_help_doc_default(self):
        exns = self.extension_registry.get_extensions(PARENT + '.help_docs')
        for hd in exns:
            if hd.label == self.name:
                return hd
        return None
            
    def perform(self, event):
        """ Perform the action by displaying the document. 
        """
        if self.my_help_doc is not None:
            filename = get_sys_prefix_relative_filename(self.my_help_doc.filename)
            if filename is not None:
                if self.my_help_doc.viewer == 'browser':
                    import webbrowser
                    try:
                        webbrowser.open(filename)
                    except (OSError, webbrowser.Error), msg:
                        logger.error('Could not open page in browser for '+\
                            'Document "%s":\n\n' % self.my_help_doc.label +\
                            msg + '\n\nTry changing Dcoument Preferences.')
                elif self.my_help_doc.viewer is not None:
                    # Run the viewer, passing it the filename
                    try:
                        Popen([self.my_help_doc.viewer, filename])
                    except OSError, msg:
                        logger.error('Could not execute program for Document' +\
                            ' "%s":\n\n ' % self.my_help_doc.label + msg +\
                            '\n\nTry changing Document Preferences.')
