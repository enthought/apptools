#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Riverbank Computing Limited
# Description: <Enthought application scripting package component>
#------------------------------------------------------------------------------


# Standard library imports.
import logging

# Enthought library imports.
from enthought.pyface.api import GUI, YES
from enthought.pyface.workbench.api import Workbench

# Local imports.
from example_script_window import ExampleScriptWindow
from model import Label


# Log to stderr.
logging.getLogger().addHandler(logging.StreamHandler())
logging.getLogger().setLevel(logging.DEBUG)


class ExampleScript(Workbench):
    """ The ExampleScript class is a workbench that creates ExampleScriptWindow
    windows.
    """

    #### 'Workbench' interface ################################################

    # The factory (in this case simply a class) that is used to create
    # workbench windows.
    window_factory = ExampleScriptWindow

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _exiting_changed(self, event):
        """ Called when the workbench is exiting. """

        if self.active_window.confirm('Ok to exit?') != YES:
            event.veto = True

        return


def main(argv):
    """ A simple example of using the the application scripting framework in a
    workbench.
    """

    # Create the GUI.
    gui = GUI()

    # Create the workbench.
    workbench = ExampleScript(state_location=gui.state_location)

    window = workbench.create_window(position=(300, 300), size=(400, 300))
    window.open()

    # Create some objects to edit.
    # FIXME v3: The need to explicitly set the style to its default value is
    # due to a bug in the implementation of Scriptable.
    label = Label(text="Label", style='normal')
    label2 = Label(text="Label2", style='normal')

    # Edit the objects.
    window.edit(label)
    window.edit(label2)

    # Start the GUI event loop.
    gui.start_event_loop()

    return


if __name__ == '__main__':
    import sys; main(sys.argv)

#### EOF ######################################################################
