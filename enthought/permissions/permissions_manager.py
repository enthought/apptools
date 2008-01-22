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
from enthought.traits.api import HasTraits, Instance

# Local imports.
from i_permissions_policy import IPermissionsPolicy
from i_user_manager import IUserManager


class PermissionsManager(HasTraits):
    """A singleton class that provides access to the current permissions
    policy and user manager."""

    #### 'PermissionsManager' interface #######################################

    # The current permissions policy.
    policy = Instance(IPermissionsPolicy)

    # The current user manager.
    user_manager = Instance(IUserManager)

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _policy_default(self):
        """Provide a default permissions policy."""

        from default.api import PermissionsPolicy

        return PermissionsPolicy()

    def _user_manager_default(self):
        """Provide a default user manager."""

        from default.api import UserManager

        return UserManager()


PermissionsManager = PermissionsManager()
