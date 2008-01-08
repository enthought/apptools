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
from enthought.traits.api import Bool, Event, Instance, Interface, List

# Local imports.
from i_user import IUser


class IUserManager(Interface):
    """The interface implemented by a user manager to manage users."""

    # Set if bootstrap permissions should be enabled.  It would normally only
    # be False if the user and permissions management is being handled by a
    # separate application.
    bootstrap_perms = Bool(True)

    # The list of PyFace user management actions implemented by this user
    # manager.
    management_actions = List(Instance(Action))

    # The current user.
    user = Instance(IUser)

    # This is fired whenever the currently authenticated user changes.  It will
    # be None if the current user isn't authenticated.
    user_authenticated = Event(IUser)

    def authenticate_user(self, user=None):
        """The user is authenticated.  The user defaults to the current user.
        Nothing is done if the user is already authenticated.  If successfully
        authenticated the user becomes the current user and all secured objects
        are re-enabled according to the user's permissions."""

    def unauthenticate_user(self):
        """Unauthenticate (ie. logout) the current user.  All secured objects
        are disabled."""
