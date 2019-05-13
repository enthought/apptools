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
from pyface.api import error
from pyface.action.api import Action
from traits.api import Dict, HasTraits, provides, Instance, List

# Local imports.
from apptools.permissions.i_policy_manager import IPolicyManager
from apptools.permissions.permission import ManagePolicyPermission, Permission
from apptools.permissions.secure_proxy import SecureProxy
from .i_policy_storage import IPolicyStorage, PolicyStorageError
from .role_assignment import role_assignment
from .role_definition import role_definition


@provides(IPolicyManager)
class PolicyManager(HasTraits):
    """The default policy manager implementation.  This policy enforces the use
    of roles.  Permissions are associated with roles rather than directly with
    users.  Users are then associated with one or more roles."""



    #### 'IPolicyManager' interface ###########################################

    management_actions = List(Instance(Action))

    user_permissions = List(Instance(Permission))

    #### 'PolicyManager' interface ############################################

    # The dictionary of registered permissions keyed on the permission name.
    permissions = Dict

    # The policy data storage.
    policy_storage = Instance(IPolicyStorage)

    ###########################################################################
    # 'IPolicyManager' interface.
    ###########################################################################

    def bootstrapping(self):
        """Return True if we are bootstrapping, ie. no roles have been defined
        or assigned."""

        try:
            bootstrap = self.policy_storage.is_empty()
        except PolicyStorageError:
            # Suppress the error and assume it isn't empty.
            bootstrap = False

        return bootstrap

    def load_policy(self, user):
        """Load the policy for the given user."""

        self.user_permissions = []

        # See if the policy is to be unloaded.
        if user is None:
            return

        # Get the user's policy.
        try:
            user_name, perm_ids = self.policy_storage.get_policy(user.name)
        except PolicyStorageError as e:
            error(None, str(e))
            return

        for id in perm_ids:
            try:
                permission = self.permissions[id]
            except KeyError:
                # This shouldn't happen if referential integrity is maintained.
                continue

            self.user_permissions.append(permission)

    def register_permission(self, permission):
        """Register the given permission."""

        if permission.id in self.permissions:
            other = self.permissions[permission.id]

            if other.application_defined:
                if permission.application_defined:
                    raise KeyError('permission "%s" has already been defined' % permission.id)

                # Use the description from the policy manager, if there is
                # one, in preference to the application supplied one.
                if permission.description:
                    other.description = permission.description
            elif permission.application_defined:
                # Again, prefer the policy manager description.
                if other.description:
                    permission.description = other.description

                self.permissions[permission.id] = permission
            else:
                # This should never happen if the policy manager is working
                # properly.
                raise KeyError('permission "%s" has already been defined by the same policy manager' % permission.id)
        else:
            self.permissions[permission.id] = permission

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _management_actions_default(self):
        """Return the management actions to manage the policy."""

        actions = []
        perm = ManagePolicyPermission()

        act = Action(name='&Role Definitions...', on_perform=role_definition)
        actions.append(SecureProxy(act, permissions=[perm], show=False))

        act = Action(name='&Role Assignments...', on_perform=role_assignment)
        actions.append(SecureProxy(act, permissions=[perm], show=False))

        return actions

    def _policy_storage_default(self):
        """Return the default storage for the policy data."""

        # Defer to an external storage manager if there is one.
        try:
            from apptools.permissions.external.policy_storage import PolicyStorage
        except ImportError:
            from apptools.permissions.default.policy_storage import PolicyStorage

        return PolicyStorage()
