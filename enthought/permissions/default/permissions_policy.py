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
from enthought.traits.api import HasTraits, implements, Instance, List

# Local imports.
from enthought.permissions.i_permissions_policy import IPermissionsPolicy
from enthought.permissions.i_permission import IPermission
from enthought.permissions.i_user_manager import IUserManager
from enthought.permissions.permission import Permission
from enthought.permissions.secure_proxy import SecureProxy
from i_management_view import IManagementView


class PermissionsPolicy(HasTraits):
    """The default permissions policy implementation.  This policy enforces the
    use of roles.  Permissions are associated with roles rather than directly
    with users.  Users are then associated with one or more roles."""

    implements(IPermissionsPolicy)

    #### 'IPermissionsPolicy' interface #######################################

    management_actions = List(Instance(Action))

    perms = List(Instance(IPermission))

    user_manager = Instance(IUserManager)

    #### 'PermissionsPolicy' interface ########################################

    management_view = Instance(IManagementView)

    ###########################################################################
    # 'IPermissionsPolicy' interface.
    ###########################################################################

    def check_perms(self, *perms):
        """TODO"""

        for perm in perms:
            # FIXME: Determine if we are in a bootstrap situation.
            if perm.bootstrap:
                return True

            if self.user_manager.user.authenticated:
                # FIXME: Check that this permissions is in the current user's
                # list.
                return True

        return False

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _management_actions_default(self):
        """Return the management actions to manage the policy."""

        update_perm = Permission(name='ets.permissions.management.update',
                description=u"Update roles and permissions", bootstrap=True)
        view_perm = Permission(name='ets.permissions.management.view',
                description=u"View roles and permissions", bootstrap=True)

        act = Action(name='&Roles and Permissions...',
                on_perform=self._manage_permissions)
        act = SecureProxy(act, perms=[update_perm, view_perm], show=False)

        return [act]

    def _user_manager_default(self):
        from user_manager import UserManager

        return UserManager()

    def _management_view_default(self):
        from management_view import ManagementView

        return ManagementView()

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _manage_permissions(self):
        """Invoke the GUI to manage the roles and permissions held by the user
        manager."""

        self.management_view(self.user_manager)
