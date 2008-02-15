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


# Standard library imports.
import errno
import socket

# Enthought library imports.
from enthought.permissions.default.api import IUserStorage, UserStorageError
from enthought.traits.api import HasTraits, implements, List, Str

# Local imports.
from proxy_server import ProxyServer


class UserStorage(HasTraits):
    """This implements a user database accessed via XML RPC."""

    implements(IUserStorage)

    #### 'IUserStorage' interface #############################################

    capabilities = List(Str)

    ###########################################################################
    # 'IUserStorage' interface.
    ###########################################################################

    def add_user(self, name, description, password):
        """Add a new user."""

        try:
            ProxyServer.add_user(name, description, password, ProxyServer.key)
        except Exception, e:
            raise UserStorageError(ProxyServer.error(e))

    def authenticate_user(self, name, password):
        """Return the tuple of the user name, description, and blob if the user
        was successfully authenticated."""

        try:
            key, name, description, blob = ProxyServer.authenticate_user(name,
                    password)

            # We don't save the cache because we should be about to read the
            # real permission ids and we do it then.
            ProxyServer.cache = description, blob, []
        except Exception, e:
            # See if we couldn't connect to the server.
            if not isinstance(e, socket.error):
                raise UserStorageError(ProxyServer.error(e))

            err, _ = e.args

            if err != errno.ECONNREFUSED:
                raise UserStorageError(ProxyServer.error(e))

            try:
                ok = ProxyServer.read_cache()
            except Exception, e:
                raise UserStorageError(str(e))

            if not ok:
                raise UserStorageError(ProxyServer.error(e))

            # We are in "disconnect" mode.
            key = None
            description, blob, _ = ProxyServer.cache

        ProxyServer.key = key

        return name, description, blob

    def delete_user(self, name):
        """Delete a new user."""

        try:
            ProxyServer.delete_user(name, ProxyServer.key)
        except Exception, e:
            raise UserStorageError(ProxyServer.error(e))

    def is_empty(self):
        """See if the database is empty."""

        # We leave it to the policy storage to answer this question.
        return False

    def matching_users(self, name):
        """Return the full name and description of all the users that match the
        given name."""

        try:
            return ProxyServer.matching_users(name, ProxyServer.key)
        except Exception, e:
            raise UserStorageError(ProxyServer.error(e))

    def modify_user(self, name, description, password):
        """Update the description and password for the given user."""

        try:
            ProxyServer.modify_user(name, description, password,
                    ProxyServer.key)
        except Exception, e:
            raise UserStorageError(ProxyServer.error(e))

    def unauthenticate_user(self, user):
        """Unauthenticate the given user."""

        if ProxyServer.key is None:
            ok = True
        else:
            try:
                ok = ProxyServer.unauthenticate_user(ProxyServer.key)
            except Exception, e:
                raise UserStorageError(ProxyServer.error(e))

        if ok:
            ProxyServer.key = ''
            ProxyServer.cache = None

        return ok

    def update_blob(self, name, blob):
        """Update the blob for the given user."""

        # Update the cache.
        description, _, perm_ids = ProxyServer.cache
        ProxyServer.cache = description, blob, perm_ids

        if ProxyServer.key is None:
            # Write the cache and tell the user about any errors.
            ProxyServer.write_cache()
        else:
            try:
                ProxyServer.update_blob(name, blob, ProxyServer.key)
            except Exception, e:
                raise UserStorageError(ProxyServer.error(e))

            # Write the cache but ignore any errors.
            try:
                ProxyServer.write_cache()
            except:
                pass

    def update_password(self, name, password):
        """Update the password for the given user."""

        # If the remote server disappeared after the capabilities were read but
        # before the user was authenticated then we could get here.
        if ProxyServer.key is None:
            raise UserStorageError("It is not possible to change password "
                    "when disconnected from the permissions server.")

        try:
            ProxyServer.update_password(name, password, ProxyServer.key)
        except Exception, e:
            raise UserStorageError(ProxyServer.error(e))

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _capabilities_default(self):
        """Return the storage capabilities."""

        try:
            caps = ProxyServer.capabilities()
        except:
            caps = []

        return caps
