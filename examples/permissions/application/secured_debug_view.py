"""The secured DebugView for the permissions framework example."""


# Enthought library imports.
from enthought.pyface.workbench.debug.api import DebugView
from enthought.permissions.api import SecureProxy

# Local imports.
from permissions import DebugViewPerm


class SecuredDebugView(DebugView):
    """A secured DebugView."""
    
    ###########################################################################
    # 'IWorkbenchPart' interface.
    ###########################################################################

    def create_control(self, parent):
        """Reimplemented to secure the created control."""

        control = DebugView.create_control(self, parent)

        return SecureProxy(control, permissions=[DebugViewPerm])

#### EOF ######################################################################
