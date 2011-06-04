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


# Enthought library imports.
from pyface.action.api import Action
from traits.api import Instance, Interface, List


class IPolicyManager(Interface):
    """The interface implemented by a policy manager.  A policy manager defines
    how permissions are assigned to users and stored.  A default policy manager
    is provided, but it may be replaced using the permissions manager."""

    # The list of PyFace policy management actions implemented by this policy.
    management_actions = List(Instance(Action))

    # The list of permissions assigned to the current user.
    user_permissions = List(Instance('apptools.permissions.api.Permission'))

    def bootstrapping(self):
        """Return True if the policy manager is bootstrapping.  Typically this
        is when no permissions have been assigned."""

    def load_user(self, user):
        """Load the policy for the given user.  user is an object that
        implements IUser.  If it is None then unload the policy for the current
        user."""

    def register_permission(self, permission):
        """Register the given permission defined by the application."""
