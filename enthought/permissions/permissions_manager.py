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
from enthought.traits.api import HasTraits, Instance

# Local imports.
from i_policy_manager import IPolicyManager
from i_user_manager import IUserManager


class PermissionsManager(HasTraits):
    """A singleton class that provides access to the current policy and user
    managers."""

    #### 'PermissionsManager' interface #######################################

    # The current policy manager.
    policy_manager = Instance(IPolicyManager)

    # The current user manager.
    user_manager = Instance(IUserManager)

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _policy_manager_default(self):
        """Provide a default policy manager."""

        from default.api import PolicyManager

        return PolicyManager()

    def _user_manager_default(self):
        """Provide a default user manager."""

        from default.api import UserManager

        return UserManager()


PermissionsManager = PermissionsManager()
