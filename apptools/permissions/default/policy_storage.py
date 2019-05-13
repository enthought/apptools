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
from traits.api import HasTraits, Instance, provides

# Local imports.
from .i_policy_storage import IPolicyStorage, PolicyStorageError
from .persistent import Persistent, PersistentError


@provides(IPolicyStorage)
class PolicyStorage(HasTraits):
    """This implements a policy database that pickles its data in a local file.
    """



    #### Private interface ####################################################

    # The persisted database.  The database itself is a tuple of the role and
    # assignment dictionaries.  The role dictionary is keyed by the role name,
    # and has a value that is a tuple of the description and the list of
    # permission names.  The assigment dictionary is keyed by the user name and
    # has a value that is the list of role names.
    _db = Instance(Persistent)

    ###########################################################################
    # 'IPolicyStorage' interface.
    ###########################################################################

    def add_role(self, name, description, perm_ids):
        """Add a new role."""

        self._db.lock()

        try:
            roles, assigns = self._db.read()

            if name in roles:
                raise PolicyStorageError("The role \"%s\" already exists." % name)

            roles[name] = (description, perm_ids)
            self._db.write((roles, assigns))
        finally:
            self._db.unlock()

    def all_roles(self):
        """Return a list of all roles."""

        roles, _ = self._readonly_copy()

        return [(name, description) for name, (description, _) in roles.items()]

    def delete_role(self, name):
        """Delete a role."""

        self._db.lock()

        try:
            roles, assigns = self._db.read()

            if name not in roles:
                raise PolicyStorageError("The role \"%s\" does not exist." % name)

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

    def get_assignment(self, user_name):
        """Return the details of the assignment for the given user name."""

        _, assigns = self._readonly_copy()

        try:
            role_names = assigns[user_name]
        except KeyError:
            return '', []

        return user_name, role_names

    def get_policy(self, user_name):
        """Return the details of the policy for the given user name."""

        roles, assigns = self._readonly_copy()

        try:
            role_names = assigns[user_name]
        except KeyError:
            return '', []

        perm_ids = []

        for r in role_names:
            _, perms = roles[r]
            perm_ids.extend(perms)

        return user_name, perm_ids

    def is_empty(self):
        """See if the database is empty."""

        roles, assigns = self._readonly_copy()

        # Both have to be non-empty for the whole thing to be non-empty.
        return (len(roles) == 0 or len(assigns) == 0)

    def matching_roles(self, name):
        """Return the full name, description and permissions of all the roles
        that match the given name."""

        roles, _ = self._readonly_copy()

        # Return any role that starts with the name.
        roles = [(full_name, description, perm_ids)
                for full_name, (description, perm_ids) in roles.items()
                        if full_name.startswith(name)]

        return sorted(roles)

    def modify_role(self, name, description, perm_ids):
        """Update the description and permissions for the given role."""

        self._db.lock()

        try:
            roles, assigns = self._db.read()

            if name not in roles:
                raise PolicyStorageError("The role \"%s\" does not exist." % name)

            roles[name] = (description, perm_ids)
            self._db.write((roles, assigns))
        finally:
            self._db.unlock()

    def set_assignment(self, user_name, role_names):
        """Save the roles assigned to a user."""

        self._db.lock()

        try:
            roles, assigns = self._db.read()

            if len(role_names) == 0:
                # Delete the user, but don't worry if there is no current
                # assignment.
                try:
                    del assigns[user_name]
                except KeyError:
                    pass
            else:
                assigns[user_name] = role_names

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
        except PersistentError as e:
            raise PolicyStorageError(str(e))

        return data

    @staticmethod
    def _db_factory():
        """Return an empty policy database."""

        return ({}, {})
