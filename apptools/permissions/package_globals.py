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


# The permissions manager.
_permissions_manager = None


def get_permissions_manager():
    """Return the IPermissionsManager implementation, creating a
    PermissionsManager instance if no other implementation has been set."""

    global _permissions_manager

    if _permissions_manager is None:
        from .permissions_manager import PermissionsManager

        _permissions_manager = PermissionsManager()

    return _permissions_manager


def set_permissions_manager(permissions_manager):
    """Set the IPermissionsManager implementation to use."""

    global _permissions_manager

    _permissions_manager = permissions_manager
