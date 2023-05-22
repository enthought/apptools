# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" A simple example of using the workbench. """


from example_workbench_window import ExampleWorkbenchWindow
from pyface.api import YES

from apptools.workbench.api import Workbench


class ExampleWorkbench(Workbench):
    """A simple example of using the workbench."""

    # 'Workbench' interface ------------------------------------------------

    # The factory (in this case simply a class!) that is used to create
    # workbench windows.
    window_factory = ExampleWorkbenchWindow

    # ------------------------------------------------------------------------
    # Private interface.
    # ------------------------------------------------------------------------

    def _exiting_changed(self, event):
        """Called when the workbench is exiting."""

        if self.confirm("Ok to exit?") != YES:
            event.veto = True

        return
