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
from i_user_storage import IUserStorage, UserStorageError
from persistent import Persistent, PersistentError


class PickledUserStorage(HasTraits):
    """This implements a user database that pickles its data in a local file.
    """

    implements(IUserStorage)

    #### 'IUserStorage' interface #############################################

    capabilities = ['user_password', 'user_add', 'user_modify', 'user_delete']

    #### Private interface ####################################################

    # The persisted database.  The database itself is a dictionary, keyed by
    # the user name, and with a value that is a tuple of the description, blob
    # and clear text password.
    _db = Instance(Persistent)

    ###########################################################################
    # 'IUserStorage' interface.
    ###########################################################################

    def add_user(self, name, description, password):
        """Add a new user."""

        self._db.lock()

        try:
            users = self._db.read()

            if users.has_key(name):
                raise UserStorageError("The user \"%s\" already exists." % name)

            users[name] = (description, '', password)
            self._db.write(users)
        finally:
            self._db.unlock()

    def delete_user(self, name):
        """Delete a user."""

        self._db.lock()

        try:
            users = self._db.read()

            if not users.has_key(name):
                raise UserStorageError("The user \"%s\" does not exist." % name)

            del users[name]
            self._db.write(users)
        finally:
            self._db.unlock()

    def get_user(self, name):
        """Return the details of the user with the given name."""

        users = self._readonly_copy()

        try:
            description, blob, password = users[name]
        except KeyError:
            return None, None, None, None

        return name, description, blob, password

    def get_users(self, name):
        """Return the full name, description, blob and password of all the
        users that match the given name."""

        # Return any user that starts with the name.
        return [(full_name, description, blob, password)
                for full_name, (description, blob, password)
                        in self._readonly_copy().items()
                        if full_name.startswith(name)]

    def is_empty(self):
        """See if the database is empty."""

        return (len(self._readonly_copy()) == 0)

    def update_blob(self, name, blob):
        """Update the blob for the given user."""

        self._db.lock()

        try:
            users = self._db.read()

            try:
                description, _, password = users[name]
            except KeyError:
                raise UserStorageError("The user \"%s\" does not exist." % name)

            users[name] = (description, blob, password)
            self._db.write(users)
        finally:
            self._db.unlock()

    def update_password(self, name, password):
        """Update the password for the given user."""

        self._db.lock()

        try:
            users = self._db.read()

            try:
                description, blob, _ = users[name]
            except KeyError:
                raise UserStorageError("The user \"%s\" does not exist." % name)

            users[name] = (description, blob, password)
            self._db.write(users)
        finally:
            self._db.unlock()

    def update_user(self, name, description, password):
        """Update the description and password for the given user."""

        self._db.lock()

        try:
            users = self._db.read()

            try:
                _, blob, _ = users[name]
            except KeyError:
                raise UserStorageError("The user \"%s\" does not exist." % name)

            users[name] = (description, blob, password)
            self._db.write(users)
        finally:
            self._db.unlock()

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def __db_default(self):
        """Return the default persisted database."""

        return Persistent(dict, 'ets_perms_userdb', "the user database")

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _readonly_copy(self):
        """Return the user database (which should not be modified)."""

        try:
            self._db.lock()

            try:
                data = self._db.read()
            finally:
                self._db.unlock()
        except PersistentError, e:
            raise UserStorageError(str(e))

        return data
