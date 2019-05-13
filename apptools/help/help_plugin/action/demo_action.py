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
from envisage.api import IExtensionPointUser, IExtensionRegistry
from pyface.workbench.action.workbench_action import WorkbenchAction
from traits.api import Instance, provides, Property
from pyface.api import ImageResource
from apptools.help.help_plugin.api import HelpCode

# Logging.
logger = logging.getLogger(__name__)

# This module's parent package.
PARENT = '.'.join(__name__.split('.')[:-2])

from .util import get_sys_prefix_relative_filename

# Implementation of the ImageResource class to be used for the DocAction class.
@provides(IExtensionPointUser)
class DemoImageResource(ImageResource):
    """ Implementation of the ImageResource class to be used for the DemoAction
    class.
    Overrides the '_image_not_found' trait in the base ImageResource class.
    """

    # Image to display when the specified image file cannot be located.
    _image_not_found = ImageResource('python_run')

class DemoAction(WorkbenchAction):
    """
    """


    ### Action interface ##############################################

    # Image associated with this action instance.
    image = Property

    ### IExtensionPointUser interface
    extension_registry = Property(Instance(IExtensionRegistry))

    def _get_extension_registry(self):
        return self.window.application.extension_registry

    def _get_image(self):
        """ Returns the image to be used for this DemoAction instance.
        """
        # The current implementation searches for an image file matching
        # 'name' in all of the image paths. If such a file is not to be found,
        # the '_image_not_found' file for the DemoImageResourceClass is used.
        return DemoImageResource(self.name)

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
            if self.my_help_code.filename:
                filename = get_sys_prefix_relative_filename(self.my_help_code.filename)
                if filename is not None:
                    try:
                        Popen([sys.executable, filename])
                    except OSError as err:
                        logger.error(
                                'Could not execute Python file for Demo "%s".\n\n' \
                                 % self.my_help_code.label + str(err) + \
                                 '\n\nTry changing Demo Preferences.' )
            elif self.my_help_code.code:
                exec("%s" % self.my_help_code.code)
        return
