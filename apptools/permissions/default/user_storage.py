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
from .i_user_storage import IUserStorage, UserStorageError
from .persistent import Persistent, PersistentError


@provides(IUserStorage)
class UserStorage(HasTraits):
    """This implements a user database that pickles its data in a local file.
    """



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

            if name in users:
                raise UserStorageError("The user \"%s\" already exists." % name)

            users[name] = (description, {}, password)
            self._db.write(users)
        finally:
            self._db.unlock()

    def authenticate_user(self, name, password):
        """Return the tuple of the user name, description, and blob if the user
        was successfully authenticated."""

        users = self._readonly_copy()

        try:
            description, blob, pword = users[name]
        except KeyError:
            raise UserStorageError("The name or password is invalid.")

        if password != pword:
            raise UserStorageError("The name or password is invalid.")

        return name, description, blob

    def delete_user(self, name):
        """Delete a user."""

        self._db.lock()

        try:
            users = self._db.read()

            try:
                del users[name]
            except KeyError:
                raise UserStorageError("The user \"%s\" does not exist." % name)

            self._db.write(users)
        finally:
            self._db.unlock()

    def is_empty(self):
        """See if the database is empty."""

        return (len(self._readonly_copy()) == 0)

    def matching_users(self, name):
        """Return the full name and description of all the users that match the
        given name."""

        # Return any user that starts with the name.
        users = [(full_name, description) for full_name, (description, _, _)
                in self._readonly_copy().items() if full_name.startswith(name)]

        return sorted(users)

    def modify_user(self, name, description, password):
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

    def unauthenticate_user(self, user):
        """Unauthenticate the given user."""

        # There is nothing to do.
        return True

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
        except PersistentError as e:
            raise UserStorageError(str(e))

        return data
