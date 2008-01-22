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
from enthought.traits.api import Interface


class PolicyStorageError(Exception):
    """This is the exception raised by an IPolicyStorage object when an error
    occurs accessing the database.  Its string representation is displayed as
    an error message to the user."""


class IPolicyStorage(Interface):
    """This defines the interface expected by a PermissionsPolicy instance to
    handle the low level storage of the user data."""

    ###########################################################################
    # 'IPolicyStorage' interface.
    ###########################################################################

    def add_role(self, role):
        """Add a new role."""

    def delete_user(self, name):
        """Delete the user with the given name (which will not be empty)."""

    def is_empty(self):
        """Return True if the user database is empty.  It will only ever be
        called once."""

    def get_user(self, name):
        """Return a tuple of the name, description, blob and password of the
        user with the given name."""

    def search_user(self, name):
        """Return a tuple of the full name, description and password of the
        user with either the given name, or the first user whose name starts
        with the given name."""

    def update_blob(self, name, blob):
        """Update the blob for the user with the given name (which will not be
        empty)."""

    def update_password(self, name, password):
        """Update the password for the user with the given name (which will not
        be empty)."""

    def update_user(self, name, description, password):
        """Update the description and password for the user with the given name
        (which will not be empty)."""

    def user_exists(self, name):
        """Return True if a user with the given name (which will not be empty)
        exists in the user database."""
