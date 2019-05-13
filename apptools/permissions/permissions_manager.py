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
from traits.api import Bool, HasTraits, Instance

# Local imports.
from .i_policy_manager import IPolicyManager
from .i_user_manager import IUserManager


class PermissionsManager(HasTraits):
    """A singleton class that provides access to the current policy and user
    managers."""

    #### 'PermissionsManager' interface #######################################

    # Set if bootstrap permissions should be automatically enabled in a
    # bootstrap situation (ie. when no policy or user data has been defined).
    # Bootstrap permissions are normally attached to actions used to define
    # policy and user data.  Normally this is True, unless policy and user data
    # is to be managed by an external application.
    allow_bootstrap_permissions = Bool(True)

    # The current policy manager.
    policy_manager = Instance(IPolicyManager)

    # The current user manager.
    user_manager = Instance(IUserManager)

    #### Private interface ####################################################

    # Set if we are bootstrapping.
    _bootstrap = Bool

    ###########################################################################
    # 'PermissionsManager' interface.
    ###########################################################################

    def check_permissions(self, *permissions):
        """Check that the current user has one or more of the given permissions
        and return True if they have.  permissions is a list of Permission
        instances."""

        # Get the current user and their assigned permissions.
        user = self.user_manager.user
        user_perms = self.policy_manager.user_permissions

        for perm in permissions:
            # If this is a bootstrap permission then see if we are in a
            # bootstrap situation.
            if perm.bootstrap and self._bootstrap:
                return True

            if user.authenticated and perm in user_perms:
                return True

        return False

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _policy_manager_default(self):
        """Provide a default policy manager."""

        # Defer to an external manager if there is one.
        try:
            from apptools.permissions.external.policy_manager import PolicyManager
        except ImportError:
            from apptools.permissions.default.policy_manager import PolicyManager

        return PolicyManager()

    def _user_manager_default(self):
        """Provide a default user manager."""

        # Defer to an external manager if there is one.
        try:
            from apptools.permissions.external.user_manager import UserManager
        except ImportError:
            from apptools.permissions.default.user_manager import UserManager

        return UserManager()

    def __bootstrap_default(self):
        """Determine whether or not we are bootstrapping.  We only want to do
        it once as checking may involve one or more remote database queries."""

        return (self.allow_bootstrap_permissions and
                (self.policy_manager.bootstrapping() or
                        self.user_manager.bootstrapping()))
