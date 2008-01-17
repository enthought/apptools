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

    # The list of PyFace management actions (ie. actions related to all users)
    # implemented by this user manager.
    management_actions = List(Instance(Action))

    # The current user.
    user = Instance(IUser)

    # The list of PyFace user actions (ie. actions related to the current user)
    # implemented by this user manager.
    user_actions = List(Instance(Action))

    # This is fired whenever the currently authenticated user changes.  It will
    # be None if the current user isn't authenticated.
    user_authenticated = Event(IUser)

    def bootstrapping(self):
        """Return True if the user manager is bootstrapping.  Typically this is
        when no users have been defined."""

    def authenticate_user(self, user=None):
        """The user is authenticated.  The user defaults to the current user.
        Nothing is done if the user is already authenticated.  If successfully
        authenticated the user becomes the current user and all secured objects
        are re-enabled according to the user's permissions."""

    def unauthenticate_user(self):
        """Unauthenticate (ie. logout) the current user.  All secured objects
        are disabled."""
