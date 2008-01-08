#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Riverbank Computing Limited
# Description: <Enthought permissions package component>
#------------------------------------------------------------------------------


# Major library imports.
from PyQt4 import QtGui

# Enthought library imports.
from enthought.permissions.api import AdapterBase


class QWidgetAdapter(AdapterBase):
    """This is the adapter for PyQt QWidget instances."""

    def adapt(self):
        """Reimplemented to adapt the proxied object."""

        # Replace the real methods.
        self.proxied.setEnabled = self.update_enabled
        self.proxied.setVisible = self.update_visible

        return self.proxied

    def get_enabled(self):
        """Get the enabled state of the proxied object."""

        return self.proxied.isEnabled()

    def set_enabled(self, value):
        """Set the enabled state of the proxied object."""

        QtGui.QWidget.setEnabled(self.proxied, value)

    def get_visible(self):
        """Get the visible state of the proxied object."""

        return self.proxied.isVisible()

    def set_visible(self, value):
        """Set the visible state of the proxied object."""

        QtGui.QWidget.setVisible(self.proxied, value)

AdapterBase.register_adapter(QWidgetAdapter, QtGui.QWidget)
