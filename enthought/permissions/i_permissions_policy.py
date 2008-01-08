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
from enthought.pyface.action.api import Action
from enthought.traits.api import Instance, Interface, List

# Local imports.
from i_permission import IPermission
from i_user_manager import IUserManager


class IPermissionsPolicy(Interface):
    """The interface implemented by a permissions policy.  A permissions policy
    completely defines how permissions and authorisation is handled.  A default
    permissions policy is provided, but it may be replaced using the
    permissions manager.
    """

    # The list of PyFace policy management actions implemented by this policy.
    management_actions = List(Instance(Action))

    # The list of all permissions that the policy enforces.
    perms = List(Instance(IPermission))

    # The user manager.  The policy uses this to add, modify and delete users.
    user_manager = Instance(IUserManager)

    def check_perms(self, *perms):
        """Check that the current user has one or more of the given
        permissions and return True if they have.  perms is a list of objects
        that implement the IPermission interface.
        """
