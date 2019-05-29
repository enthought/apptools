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
from traits.api import Bool, Instance, Interface

# Local imports.
from .i_user_storage import IUserStorage


class IUserDatabase(Interface):
    """The interface to be implemented by a user database for the default user
    manager."""

    # Set if the implementation supports changing a user's password.
    can_change_password = Bool

    # Set if the implementation supports adding users.
    can_add_user = Bool

    # Set if the implementation supports modifying users.
    can_modify_user = Bool

    # Set if the implementation supports deleting users.
    can_delete_user = Bool

    # The user data storage.
    user_storage = Instance(IUserStorage)

    def bootstrapping(self):
        """Return True if the user database is bootstrapping.  Typically this
        is when no users have been defined."""

    def authenticate_user(self, user):
        """Authenticate the given user and return True if successful.  user
        implements IUser."""

    def unauthenticate_user(self, user):
        """Unauthenticate the given user and return True if successful.  user
        implements IUser."""

    def change_password(self, user):
        """Change a user's password in the database.  This only needs to be
        reimplemented if 'can_change_password' is True."""

    def add_user(self):
        """Add a user account to the database.  This only needs to be
        reimplemented if 'can_add_user' is True."""

    def modify_user(self):
        """Modify a user account in the database.  This only needs to be
        reimplemented if 'can_modify_user' is True."""

    def delete_user(self):
        """Delete a user account from the database.  This only needs to be
        reimplemented if 'can_delete_user' is True."""

    def matching_user(self, name):
        """Return an object that implements IUser for the user selected based
        on the given name.  If there was no user selected then return None.
        How the name is interpreted (eg. as a regular expression) is determined
        by the user database.  Note that the blob attribute of the user will
        not be set."""

    def user_factory(self):
        """Return a new object that implements the IUser interface."""
