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
from enthought.pyface.action.api import Action
from enthought.traits.api import Bool, HasTraits, implements, Instance, List

# Local imports.
from enthought.permissions.i_permission import IPermission
from enthought.permissions.permission import Permission
from enthought.permissions.i_policy_manager import IPolicyManager
from enthought.permissions.permissions_manager import PermissionsManager
from enthought.permissions.secure_proxy import SecureProxy
from i_policy_storage import IPolicyStorage
from policy_data import Assignment, Role
from role_definition import role_definition


class PolicyManager(HasTraits):
    """The default policy manager implementation.  This policy enforces the use
    of roles.  Permissions are associated with roles rather than directly with
    users.  Users are then associated with one or more roles."""

    implements(IPolicyManager)

    #### 'IPolicyManager' interface ###########################################

    allow_bootstrap_perms = Bool(True)

    management_actions = List(Instance(Action))

    perms = List(Instance(IPermission))

    #### 'PolicyManager' interface ############################################

    # The list of roles.
    roles = List(Instance(Role))

    # The list of assignments.
    assignments = List(Instance(Assignment))

    # The policy data storage.
    policy_storage = Instance(IPolicyStorage)

    ###########################################################################
    # 'IPolicyManager' interface.
    ###########################################################################

    def check_perms(self, *perms):
        """TODO"""

        # Get the current user.
        user = PermissionsManager.user_manager.user

        for perm in perms:
            # If this is a bootstrap permission then see if we are in a
            # bootstrap situation.
            if perm.bootstrap and self.allow_bootstrap_perms and self._bootstrapping():
                return True

            if user.authenticated:
                # FIXME: Check that this permissions is in the current user's
                # list.
                return True

        return False

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _management_actions_default(self):
        """Return the management actions to manage the policy."""

        actions = []

        perm = Permission(name='ets.permissions.management.define_roles',
                description=u"Define roles", bootstrap=True)
        act = Action(name='&Role Definitions...',
                on_perform=lambda: role_definition(self))

        actions.append(SecureProxy(act, perms=[perm], show=False))

        perm = Permission(name='ets.permissions.management.assign_roles',
                description=u"Assignment Roles", bootstrap=True)
        act = Action(name='&Role Assignments...', on_perform=self._assign_role)

        actions.append(SecureProxy(act, perms=[perm], show=False))

        return actions

    def _policy_storage_default(self):
        """Return the default storage for the policy data."""

        from pickled_policy_storage import PickledPolicyStorage

        return PickledPolicyStorage()

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _bootstrapping(self):
        """Return True if we are bootstrapping, ie. no policy or user data
        exists."""

        if PermissionsManager.user_manager.bootstrapping():
            return True

        # FIXME: Check for policy data.
        return True

    def _assign_role(self):
        """Assign the roles."""

        from enthought.pyface.api import information

        information(None, "This will eventually implement a TraitsUI based GUI for assigning roles.")
