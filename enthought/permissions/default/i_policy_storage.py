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
from traits.api import Interface


class PolicyStorageError(Exception):
    """This is the exception raised by an IPolicyStorage object when an error
    occurs accessing the database.  Its string representation is displayed as
    an error message to the user."""


class IPolicyStorage(Interface):
    """This defines the interface expected by a PolicyManager to handle the low
    level storage of the policy data."""

    ###########################################################################
    # 'IPolicyStorage' interface.
    ###########################################################################

    def add_role(self, name, description, perm_ids):
        """Add a new role."""

    def all_roles(self):
        """Return a list of all roles where each element is a tuple of the name
        and description."""

    def delete_role(self, name):
        """Delete the role with the given name (which will not be empty)."""

    def get_assignment(self, user_name):
        """Return a tuple of the user name and list of role names of the
        assignment for the given user name.  The tuple will contain an empty
        string and list if the user isn't known."""

    def get_policy(self, user_name):
        """Return a tuple of the user name and list of permission names for the
        user with the given name.  The tuple will contain an empty string and
        list if the user isn't known."""

    def is_empty(self):
        """Return True if the user database is empty.  It will only ever be
        called once."""

    def matching_roles(self, name):
        """Return a list of tuples of the full name, description and list of
        permission names, sorted by the full name, of all roles that match the
        given name.  How the name is interpreted (eg. as a regular expression)
        is determined by the storage."""

    def modify_role(self, name, description, perm_ids):
        """Update the description and permissions for the role with the given
        name (which will not be empty)."""

    def set_assignment(self, user_name, role_names):
        """Save the assignment of the given role names to the given user.  Note
        that there may or may not be an existing assignment for the user."""
