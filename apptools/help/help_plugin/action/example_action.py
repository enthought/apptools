""" (Pyface) Action for displaying a help example.

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
from subprocess import Popen

# Enthought library imports.
from envisage.api import IExtensionPointUser, IExtensionRegistry
from pyface.workbench.action.workbench_action import WorkbenchAction
from traits.api import Instance, provides, Property

from apptools.help.help_plugin.api import HelpCode
from apptools.help.help_plugin.examples_preferences import \
    ExamplesPreferences

# Local import
from .util import get_sys_prefix_relative_filename

# Logging.
logger = logging.getLogger(__name__)

# This module's parent package.
PARENT = '.'.join(__name__.split('.')[:-2])

@provides(IExtensionPointUser)
class ExampleAction(WorkbenchAction):
    """ (Pyface) Action for displaying a help example.
    """


    ### IExtensionPointUser interface
    extension_registry = Property(Instance(IExtensionRegistry))

    def _get_extension_registry(self):
        return self.window.application.extension_registry

    ### HelpExampleAction interface

    # Help code associated with this action.
    my_help_code = Instance(HelpCode)

    # Preferences for examples
    preferences = Instance(ExamplesPreferences)

    def _my_help_code_default(self):
        exns = self.extension_registry.get_extensions(PARENT + '.help_examples')
        for he in exns:
            if he.label == self.name:
                return he
        return None

    def perform(self, event):
        """ Perform the action by displaying the document.
        """
        if self.my_help_code is not None:
            filename = get_sys_prefix_relative_filename(self.my_help_code.filename)
            if filename is not None:
                logger.info('Perform ExampleAction on %s' % filename)
                if self.preferences.editor is not None:
                    # Run the editor, passing it the filename
                    try:
                        Popen([self.preferences.editor, filename])
                    except OSError as err:
                        logger.error(
                        'Could not execute program for Example "%s":\n\n ' \
                        % self.my_help_code.label + str(err) + '\n\nTry ' +\
                        'changing Examples Preferences.')
