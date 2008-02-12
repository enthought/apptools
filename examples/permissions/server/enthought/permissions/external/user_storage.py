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
from enthought.permissions.default.api import IUserStorage, UserStorageError
from enthought.traits.api import HasTraits, implements, Instance, List, Str

# Local imports.
from proxy_server import ProxyServer


class UserStorage(HasTraits):
    """This implements a user database accessed via XML RPC."""

    implements(IUserStorage)

    #### 'IUserStorage' interface #############################################

    capabilities = List(Str)

    #### Private interface ####################################################

    # The proxy for the XML RPC server.
    _server = Instance(ProxyServer)

    ###########################################################################
    # 'IUserStorage' interface.
    ###########################################################################

    def add_user(self, name, description, password):
        """Add a new user."""

        try:
            # FIXME: Need to pass session key.
            self._server.add_user(name, description, password)
        except Exception, e:
            raise UserStorageError(self._server.error(e))

    def authenticate_user(self, name, password):
        """Return the tuple of the user name, description, and blob if the user
        was successfully authenticated."""

        try:
            # FIXME: Handle the session key when it is returned.
            return self._server.authenticate_user(name, password)
        except Exception, e:
            raise UserStorageError(self._server.error(e))

    def delete_user(self, name):
        """Delete a new user."""

        try:
            # FIXME: Need to pass session key.
            self._server.delete_user(name)
        except Exception, e:
            raise UserStorageError(self._server.error(e))

    def is_empty(self):
        """See if the database is empty."""

        # We leave it to the policy storage to answer this question.
        return False

    def matching_users(self, name):
        """Return the full name and description of all the users that match the
        given name."""

        try:
            # FIXME: Need to pass session key.
            return self._server.matching_users(name)
        except Exception, e:
            raise UserStorageError(self._server.error(e))

    def modify_user(self, name, description, password):
        """Update the description and password for the given user."""

        try:
            # FIXME: Need to pass session key.
            self._server.modify_user(name, description, password)
        except Exception, e:
            raise UserStorageError(self._server.error(e))

    def unauthenticate_user(self, user):
        """Unauthenticate the given user."""

        try:
            # FIXME: Need to pass session key.
            return self._server.unauthenticate_user()
        except Exception, e:
            raise UserStorageError(self._server.error(e))

    def update_blob(self, name, blob):
        """Update the blob for the given user."""

        try:
            # FIXME: Need to pass session key.
            self._server.update_blob(name, blob)
        except Exception, e:
            raise UserStorageError(self._server.error(e))

    def update_password(self, name, password):
        """Update the password for the given user."""

        try:
            # FIXME: Need to pass session key.
            self._server.update_password(name, password)
        except Exception, e:
            raise UserStorageError(self._server.error(e))

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _capabilities_default(self):
        """Return the storage capabilities."""

        try:
            caps = self._server.capabilities()
        except:
            caps = []

        return caps

    def __server_default(self):
        """Return the default proxy server."""

        return ProxyServer()
