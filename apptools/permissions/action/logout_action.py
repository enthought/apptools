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
from traits.api import Bool, Unicode

# Local imports.
from apptools.permissions.package_globals import get_permissions_manager


class LogoutAction(Action):
    """An action that unauthenticates the current user."""

    #### 'Action' interface ###################################################

    enabled = Bool(False)

    name = Unicode("Log&out")

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **traits):
        """Initialise the object."""

        super(LogoutAction, self).__init__(**traits)

        get_permissions_manager().user_manager.on_trait_event(self._refresh_enabled, 'user_authenticated')

    ###########################################################################
    # 'Action' interface.
    ###########################################################################

    def perform(self, event):
        """Perform the action."""

        get_permissions_manager().user_manager.unauthenticate_user()

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _refresh_enabled(self, user):
        """Invoked whenever the current user's authorisation state changes."""

        self.enabled = user is not None
