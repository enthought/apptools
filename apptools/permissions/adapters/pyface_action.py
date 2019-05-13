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


# Enthought library imports.
from apptools.permissions.adapter_base import AdapterBase
from pyface.action.api import Action


class ActionAdapter(AdapterBase):
    """This is the adapter for PyFace actions."""

    def get_enabled(self):
        """Get the enabled state of the proxied object."""

        return self.proxied.enabled

    def set_enabled(self, value):
        """Set the enabled state of the proxied object."""

        self.proxied.enabled = value

    def get_visible(self):
        """Get the visible state of the proxied object."""

        return self.proxied.visible

    def set_visible(self, value):
        """Set the visible state of the proxied object."""

        self.proxied.visible = value

    def setattr(self, name, value):
        """Reimplemented to intercept the setting of the enabled and visible
        attributes of the proxied action.
        """

        if name == 'enabled':
            self.update_enabled(value)
        elif name == 'visible':
            self.update_visible(value)
        else:
            super(ActionAdapter, self).setattr(name, value)

AdapterBase.register_adapter(ActionAdapter, Action)
