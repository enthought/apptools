""" Abstract base class for all workbench actions. """


# Enthought library imports.
from pyface.action.api import Action
from traits.api import Instance

from apptools.workbench.api import WorkbenchWindow


class WorkbenchAction(Action):
    """ Abstract base class for all workbench actions. """

    #### 'WorkbenchAction' interface ##########################################

    # The workbench window that the action is in.
    #
    # This is set by the framework.
    window = Instance(WorkbenchWindow)
