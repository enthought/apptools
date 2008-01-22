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
from enthought.traits.api import Unicode

# Local imports.
from enthought.permissions.permissions_manager import PermissionsManager


class LoginAction(Action):
    """An action that authenticates the current user."""

    #### 'Action' interface ###################################################

    name = Unicode("Log&in...")

    ###########################################################################
    # 'Action' interface.
    ###########################################################################

    def perform(self, event):
        """Perform the action."""

        PermissionsManager.user_manager.authenticate_user()
