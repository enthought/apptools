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
# Description: <Enthought permissions package component>
#------------------------------------------------------------------------------


# Major library imports.
import wx

# Enthought library imports.
from apptools.permissions.adapter_base import AdapterBase


class wxWindowAdapter(AdapterBase):
    """This is the adapter for wx Window instances."""

    def adapt(self):
        """Reimplemented to adapt the proxied object."""

        # Replace the real methods.
        self.proxied.Enable = self.update_enabled
        self.proxied.Show = self.update_visible

        return self.proxied

    def get_enabled(self):
        """Get the enabled state of the proxied object."""

        return self.proxied.IsEnabled()

    def set_enabled(self, value):
        """Set the enabled state of the proxied object."""

        wx.Window.Enable(self.proxied, value)

    def get_visible(self):
        """Get the visible state of the proxied object."""

        return self.proxied.IsShown()

    def set_visible(self, value):
        """Set the visible state of the proxied object."""

        wx.Window.Show(self.proxied, value)

AdapterBase.register_adapter(wxWindowAdapter, wx.Window)
