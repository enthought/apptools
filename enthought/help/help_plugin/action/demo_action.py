""" (Pyface) Action for running a help demo.

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

from enthought.help.help_plugin.api import HelpCode

# Logging.
logger = logging.getLogger(__name__)

# This module's parent package.
PARENT = '.'.join(__name__.split('.')[:-2])

from util import get_sys_prefix_relative_filename

class DemoAction(WorkbenchAction):
    """
    """
    implements(IExtensionPointUser)
    
    ### IExtensionPointUser interface
    extension_registry = Property(Instance(IExtensionRegistry))
    
    def _get_extension_registry(self):
        return self.window.application.extension_registry
    
    ### HelpDemoAction interface
    
    # Help code associated with this action.
    my_help_code = Instance(HelpCode)
    
    def _my_help_code_default(self):
        exns = self.extension_registry.get_extensions(PARENT + '.help_demos')
        for hc in exns:
            if hc.label == self.name:
                return hc
        return None
            
    def perform(self, event):
        """ Perform the action by running the demo. 
        """
        if self.my_help_code is not None:
            filename = get_sys_prefix_relative_filename(self.my_help_code.filename)
            if filename is not None:
                try:
                    Popen([sys.executable, filename])
                except OSError, err:
                    logger.error(
                        'Could not execute Python file for Demo "%s".\n\n' \
                        % self.my_help_code.label + str(err) + \
                        '\n\nTry changing Demo Preferences.' )
