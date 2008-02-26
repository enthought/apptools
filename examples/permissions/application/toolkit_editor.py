"""An editor implemented by a toolkit specific widget.  This demonstrates the
ability to apply permissions to toolkit specific widgets.
"""


# Enthought library imports.
from enthought.etsconfig.api import ETSConfig
from enthought.permissions.api import SecureProxy
from enthought.pyface.workbench.api import Editor

# Local imports.
from permissions import EnableWidgetPerm


class ToolkitEditor(Editor):
    """A workbench editor that displays string with a permission attached to
    the toolkit widget.
    """

    def create_control(self, parent):
        """Create the toolkit specific control."""

        tk = ETSConfig.toolkit

        if tk == 'wx':
            import wx

            control = wx.StaticText(parent, -1, self.obj,
                    style=wx.ALIGN_CENTER)
        elif tk == 'qt4':
            from PyQt4 import QtCore, QtGui

            control = QtGui.QLabel(self.obj, parent)
            control.setAlignment(QtCore.Qt.AlignHCenter)
        else:
            raise ValueError, "unsupported toolkit: %s" % tk

        # Return the wrapped control.
        return SecureProxy(control, [EnableWidgetPerm])

    def destroy_control(self):
        """Create the toolkit specific control."""

        tk = ETSConfig.toolkit

        if tk == 'wx':
            self.control.Destroy()
        elif tk == 'qt4':
            self.control.setParent(None)

    def _name_default(self):
        """Show the toolkit in the editor name."""

        return str(self)

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __str__(self):
        """Return an informal string representation of the object."""

        return ETSConfig.toolkit + " Editor"

#### EOF ######################################################################
