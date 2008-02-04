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
from enthought.permissions.default.api import IPolicyStorage, \
        PolicyStorageError
from enthought.traits.api import HasTraits, implements, Instance

# Local imports.
from proxy_server import ProxyServer


class XMLRPCPolicyStorage(HasTraits):
    """This implements a policy database accessed via XML RPC."""

    implements(IPolicyStorage)

    #### Private interface ####################################################

    # The proxy for the XML RPC server.
    _server = Instance(ProxyServer)

    ###########################################################################
    # 'IPolicyStorage' interface.
    ###########################################################################

    def add_role(self, name, description, perm_names):
        """Add a new role."""

        try:
            # FIXME: Need to pass session key.
            self._server.add_role(name, description, perm_names)
        except Exception, e:
            raise PolicyStorageError(self._server.error(e))

    def all_roles(self):
        """Return a list of all roles."""

        try:
            # FIXME: Need to pass session key.
            return self._server.all_roles()
        except Exception, e:
            raise PolicyStorageError(self._server.error(e))

    def delete_role(self, name):
        """Delete a role."""

        try:
            # FIXME: Need to pass session key.
            self._server.delete_role(name)
        except Exception, e:
            raise PolicyStorageError(self._server.error(e))

    def get_assignment(self, user_name):
        """Return the details of the assignment for the given user name."""

        try:
            # FIXME: Need to pass session key.
            return self._server.get_assignment(user_name)
        except Exception, e:
            raise PolicyStorageError(self._server.error(e))

    def get_policy(self, user_name):
        """Return the details of the policy for the given user name."""

        try:
            # FIXME: Need to pass session key.
            return self._server.get_policy(user_name)
        except Exception, e:
            raise PolicyStorageError(self._server.error(e))

    def is_empty(self):
        """See if the database is empty."""

        try:
            return self._server.is_empty_policy()
        except Exception, e:
            raise PolicyStorageError(self._server.error(e))

    def matching_roles(self, name):
        """Return the full name, description and permissions of all the roles
        that match the given name."""

        try:
            # FIXME: Need to pass session key.
            return self._server.matching_roles(name)
        except Exception, e:
            raise PolicyStorageError(self._server.error(e))

    def modify_role(self, name, description, perm_names):
        """Update the description and permissions for the given role."""

        try:
            # FIXME: Need to pass session key.
            self._server.update_role(name, description, perm_names)
        except Exception, e:
            raise PolicyStorageError(self._server.error(e))

    def set_assignment(self, user_name, role_names):
        """Save the roles assigned to a user."""

        try:
            # FIXME: Need to pass session key.
            self._server.set_assignment(user_name, role_names)
        except Exception, e:
            raise PolicyStorageError(self._server.error(e))

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def __server_default(self):
        """Return the default proxy server."""

        return ProxyServer()
