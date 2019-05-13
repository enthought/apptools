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
from envisage.api import IExtensionPointUser, IExtensionRegistry
from pyface.workbench.action.workbench_action import WorkbenchAction
from traits.api import Instance, provides, Property
from pyface.api import ImageResource

from apptools.help.help_plugin.api import HelpDoc

# Local imports
from .util import get_sys_prefix_relative_filename

# Logging.
logger = logging.getLogger(__name__)

# This module's parent package.
PARENT = '.'.join(__name__.split('.')[:-2])

# Implementation of the ImageResource class to be used for the DocAction class.
@provides(IExtensionPointUser)
class DocImageResource(ImageResource):
    """ Implementation of the ImageResource class to be used for the DocAction
    class.
    Overrides the '_image_not_found' trait in the base ImageResource class.
    """

    _image_not_found = ImageResource('document')

class DocAction(WorkbenchAction):
    """ (Pyface) Action for displaying a help doc.
    """


    ### Action interface ##############################################

    # Image associated with this action instance.
    image = Property

    ### IExtensionPointUser interface

    extension_registry = Property(Instance(IExtensionRegistry))

    def _get_extension_registry(self):
        return self.window.application.extension_registry

    def _get_image(self):
        """ Returns the image to be used for this DocAction instance.
        """
        # The current implementation searches for an image file matching
        # 'name' in all of the image paths. If such a file is not to be found,
        # the '_image_not_found' file for the DocImageResourceClass is used.
        return DocImageResource(self.name)

    ### HelpDocAction interface

    # Help doc associated with this action.
    my_help_doc = Instance(HelpDoc)

    def _my_help_doc_default(self):
        exns = self.extension_registry.get_extensions(PARENT + '.help_docs')
        for hd in exns:
            if hd.label == self.name:
                return hd
        return None

    def _get_filename(self, doc):
        filename = None
        if doc is not None:
            if doc.url:
                filename = doc.filename
            else:
                filename = get_sys_prefix_relative_filename(doc.filename)
        return filename

    def perform(self, event):
        """ Perform the action by displaying the document.
        """

        filename = self._get_filename(self.my_help_doc)
        if filename is not None:
            if self.my_help_doc.url or self.my_help_doc.viewer == 'browser':
                import webbrowser
                try:
                    webbrowser.open(filename)
                except (OSError, webbrowser.Error) as msg:
                    logger.error('Could not open page in browser for '+ \
                        'Document "%s":\n\n' % self.my_help_doc.label + \
                        str(msg) + '\n\nTry changing Dcoument Preferences.')
            elif self.my_help_doc.viewer is not None:
                # Run the viewer, passing it the filename
                try:
                    Popen([self.my_help_doc.viewer, filename])
                except OSError as msg:
                    logger.error('Could not execute program for Document' + \
                        ' "%s":\n\n ' % self.my_help_doc.label + str(msg) + \
                        '\n\nTry changing Document Preferences.')
