"""A simple example of using the permissions framework."""


# Standard library imports.
import logging

# Enthought library imports.
from enthought.pyface.api import GUI, YES
from enthought.pyface.workbench.api import Workbench

# Local imports.
from workbench_window import ExampleWorkbenchWindow
from person import Person


# Log to stderr.
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class ExampleWorkbench(Workbench):
    """A simple example of using the workbench."""

    #### 'Workbench' interface ################################################

    # The factory (in this case simply a class) that is used to create
    # workbench windows.
    window_factory = ExampleWorkbenchWindow

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _exiting_changed(self, event):
        """Called when the workbench is exiting."""

        if self.active_window.confirm('Ok to exit?') != YES:
            event.veto = True


def main(argv):
    """A simple example of using the workbench."""

    # Create the GUI.
    gui = GUI()

    # Create the workbench.
    #
    # fixme: I wouldn't really want to specify the state location here.
    # Ideally this would be part of the GUI's as DOMs idea, and the state
    # location would be an attribute picked up from the DOM hierarchy. This
    # would also be the mechanism for doing 'confirm' etc... Let the request
    # bubble up the DOM until somebody handles it.
    workbench = ExampleWorkbench(state_location=gui.state_location)

    # Create the workbench window.
    window = workbench.create_window(position=(300, 300), size=(800, 600))
    window.open()

    # This will cause a TraitsUI editor to be created.
    window.edit(Person(name='fred', age=42, salary=50000))

    # This will cause a toolkit specific editor to be created.
    window.edit("This text is implemented by a toolkit specific widget.")

    # Start the GUI event loop.
    gui.start_event_loop()


if __name__ == '__main__':
    import sys; main(sys.argv)

#### EOF ######################################################################
