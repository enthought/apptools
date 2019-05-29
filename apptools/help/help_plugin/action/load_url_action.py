""" (Pyface) Action for running a help demo.

    :Copyright: 2009, Enthought Inc.
    :License: BSD
    :Author: Vibha Srinivasan
"""
# This software is provided without warranty under the terms of the BSD
# license included in AppTools/trunk/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!

# Local imports.
from .doc_action import DocAction

# This module's parent package.
PARENT = '.'.join(__name__.split('.')[:-2])


class LoadURLAction(DocAction):
    """ Workbench Action for displaying a url in a web browser.
    """

    def _my_help_doc_default(self):
        exns = self.extension_registry.get_extensions(PARENT +
                                                      '.help_downloads')
        for hc in exns:
            if hc.label == self.name:
                return hc
        return None
