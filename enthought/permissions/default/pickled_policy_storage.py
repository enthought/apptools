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
from enthought.traits.api import HasTraits, Instance, implements

# Local imports.
from i_policy_storage import IPolicyStorage, PolicyStorageError
from persistent import Persistent, PersistentError


class PickledPolicyStorage(HasTraits):
    """This implements a user database that pickles its data in a local file.
    """

    implements(IPolicyStorage)

    #### Private interface ###################################################

    # The persisted database.  The database itself is a tuple of the role and
    # assignment dictionaries.  The role dictionary is keyed by the role name,
    # and has a value that is a tuple of the description and the list of
    # permission names.  The assigment dictionary is keyed by the user name and
    # has a value that is the list of role names.
    _db = Instance(Persistent)

    ###########################################################################
    # 'IPolicyStorage' interface.
    ###########################################################################

    def add_role(self, name, description, perm_names):
        """Add a new role."""

        self._db.lock()

        try:
            roles, assigns = self._db.read()

            if roles.has_key(name):
                raise PolicyStorageError("The role \"%s\" already exists." % name)

            roles[name] = (description, perm_names)
            self._db.write((roles, assigns))
        finally:
            self._db.unlock()

    def delete_role(self, name):
        """Delete a role."""

        self._db.lock()

        try:
            roles, assigns = self._db.read()

            if not roles.has_key(name):
                raise PolicyStorageError("The role \"%s\" doesn't exist." % name)

            del roles[name]

            # Remove the role from any users who have it.
            for user, role_names in assigns.items():
                try:
                    role_names.remove(name)
                except ValueError:
                    continue

                assigns[user] = role_names

            self._db.write((roles, assigns))
        finally:
            self._db.unlock()

    def is_empty(self):
        """See if the database is empty."""

        roles, assigns = self._readonly_copy()

        # Both have to be non-empty for the whole thing to be non-empty.
        return (len(roles) == 0 or len(assigns) == 0)

    def search_role(self, name):
        """Return the full name, description and permissions of the role with
        the given name, or one that starts with the given name."""

        roles, _ = self._readonly_copy()

        # Try the exact name first.
        try:
            description, perm_names = roles[name]
        except KeyError:
            # Find the first user that starts with the name.
            for n, (description, perm_names) in roles.items():
                if n.startswith(name):
                    name = n
                    break
            else:
                return None, None, None

        return name, description, perm_names

    def update_role(self, name, description, perm_names):
        """Update the description and permissions for the given role."""

        self._db.lock()

        try:
            roles, assigns = self._db.read()

            roles[name] = (description, perm_names)
            self._db.write((roles, assigns))
        finally:
            self._db.unlock()

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def __db_default(self):
        """Return the default persisted database."""

        return Persistent(self._db_factory, 'ets_perms_policydb',
                "the policy database")

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _readonly_copy(self):
        """Return the policy database (which should not be modified)."""

        try:
            self._db.lock()

            try:
                data = self._db.read()
            finally:
                self._db.unlock()
        except PersistentError, e:
            raise PolicyStorageError(str(e))

        return data

    @staticmethod
    def _db_factory():
        """Return an empty policy database."""

        return ({}, {})
