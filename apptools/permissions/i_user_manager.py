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
from pyface.action.api import Action
from traits.api import Bool, Event, Instance, Interface, List

# Local imports.
from .i_user import IUser


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

    def authenticate_user(self):
        """Authenticate (ie. login) the user.  If successfully authenticated
        all secured objects are re-enabled according to the user's permissions.
        """

    def unauthenticate_user(self):
        """Unauthenticate (ie. logout) the user.  All secured objects are
        disabled."""

    def select_user(self, name):
        """Return an object that implements IUser for the user selected based
        on the given name.  If there was no user selected then return None.
        How the name is interpreted (eg. as a regular expression) is determined
        by the user manager."""
