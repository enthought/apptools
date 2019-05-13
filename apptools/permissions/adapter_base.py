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
from traits.api import Any, Bool, HasTraits, Instance, List

# Local imports.
from .package_globals import get_permissions_manager
from .permission import Permission


class AdapterBase(HasTraits):
    """This is the base class for object specific adapters."""

    # The object being proxied.
    proxied = Any

    # The list of permissions applied to the proxied object.
    permissions = List(Instance(Permission))

    # Set if the proxied object should be shown when it is enabled.
    show = Bool

    # The desired enabled state of the proxied object, ie. the state set by the
    # application before any permissions were applied.
    _desired_enabled = Bool

    # The desired visible state of the proxied object, ie. the state set by the
    # application before any permissions were applied.
    _desired_visible = Bool

    # The registered adapter types.
    _adapter_types = {}

    @classmethod
    def register_adapter(cls, adapter, *types):
        """Register an adapter type for one or more object types."""

        for t in types:
            cls._adapter_types[t] = adapter

    @classmethod
    def factory(cls, proxied, permissions, show):
        """Return an adapter for the proxied object.  permissions is a list of
        permissions to attach to the object.  show is set if the proxied object
        should be visible when it is disabled.
        """

        # Find a suitable adapter type.
        for object_type, adapter_type in cls._adapter_types.items():
            if isinstance(proxied, object_type):
                break
        else:
            raise TypeError("no SecureProxy adapter registered for %s" % proxied)

        adapter = adapter_type(proxied=proxied, permissions=permissions,
                show=show)

        # Refresh the state of the object when the authentication state of the
        # current user changes.
        get_permissions_manager().user_manager.on_trait_event(adapter._refresh,
                'user_authenticated')

        return adapter

    def adapt(self):
        """Try and adapt the proxied object and return the adapted object if
        successful.  If None is returned a proxy wrapper will be created.
        """

        return None

    def setattr(self, name, value):
        """The default implementation to set an attribute of the proxied
        object.
        """

        setattr(self.proxied, name, value)

    def get_enabled(self):
        """Get the enabled state of the proxied object."""

        raise NotImplementedError

    def set_enabled(self, value):
        """Set the enabled state of the proxied object."""

        raise NotImplementedError

    def update_enabled(self, value):
        """Update the proxied object after a possible new value of the enabled
        attribute.
        """

        if get_permissions_manager().check_permissions(*self.permissions):
            self.set_enabled(value)

            if not self.show:
                self.set_visible(self._desired_visible)
        else:
            self.set_enabled(False)

            if not self.show:
                self.set_visible(False)

        # Save the desired value so that it can be checked if the user becomes
        # authenticated.
        self._desired_enabled = value

    def get_visible(self):
        """Get the visible state of the proxied object."""

        raise NotImplementedError

    def set_visible(self, value):
        """Set the visible state of the proxied object."""

        raise NotImplementedError

    def update_visible(self, value):
        """Update the proxied object after a possible new value of the visible
        attribute.
        """

        if self.show:
            self.set_visible(value)
        elif get_permissions_manager().check_permissions(*self.permissions):
            self.set_visible(value)
        else:
            self.set_visible(False)

        # Save the desired value so that it can be checked if the user becomes
        # authenticated.
        self._desired_visible = value

    def _refresh(self, user):
        """Invoked whenever the current user's authorisation state changes."""

        if not self.show:
            self.update_visible(self._desired_visible)

        self.update_enabled(self._desired_enabled)
