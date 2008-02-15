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
from enthought.traits.api import HasTraits, implements

# Local imports.
from proxy_server import ProxyServer


class PolicyStorage(HasTraits):
    """This implements a policy database accessed via XML RPC."""

    implements(IPolicyStorage)

    ###########################################################################
    # 'IPolicyStorage' interface.
    ###########################################################################

    def add_role(self, name, description, perm_ids):
        """Add a new role."""

        try:
            ProxyServer.add_role(name, description, perm_ids, ProxyServer.key)
        except Exception, e:
            raise PolicyStorageError(ProxyServer.error(e))

    def all_roles(self):
        """Return a list of all roles."""

        try:
            return ProxyServer.all_roles(ProxyServer.key)
        except Exception, e:
            raise PolicyStorageError(ProxyServer.error(e))

    def delete_role(self, name):
        """Delete a role."""

        try:
            ProxyServer.delete_role(name, ProxyServer.key)
        except Exception, e:
            raise PolicyStorageError(ProxyServer.error(e))

    def get_assignment(self, user_name):
        """Return the details of the assignment for the given user name."""

        try:
            return ProxyServer.get_assignment(user_name, ProxyServer.key)
        except Exception, e:
            raise PolicyStorageError(ProxyServer.error(e))

    def get_policy(self, name):
        """Return the details of the policy for the given user name."""

        description, blob, perm_ids = ProxyServer.cache

        if ProxyServer.key is not None:
            try:
                name, perm_ids = ProxyServer.get_policy(name, ProxyServer.key)
            except Exception, e:
                raise PolicyStorageError(ProxyServer.error(e))

            # Save the permissions ids in the persistent cache.
            ProxyServer.cache = description, blob, perm_ids

            try:
                ProxyServer.write_cache()
            except:
                pass

        return name, perm_ids

    def is_empty(self):
        """See if the database is empty."""

        try:
            return ProxyServer.is_empty_policy()
        except Exception, e:
            raise PolicyStorageError(ProxyServer.error(e))

    def matching_roles(self, name):
        """Return the full name, description and permissions of all the roles
        that match the given name."""

        try:
            return ProxyServer.matching_roles(name, ProxyServer.key)
        except Exception, e:
            raise PolicyStorageError(ProxyServer.error(e))

    def modify_role(self, name, description, perm_ids):
        """Update the description and permissions for the given role."""

        try:
            ProxyServer.modify_role(name, description, perm_ids,
                    ProxyServer.key)
        except Exception, e:
            raise PolicyStorageError(ProxyServer.error(e))

    def set_assignment(self, user_name, role_names):
        """Save the roles assigned to a user."""

        try:
            ProxyServer.set_assignment(user_name, role_names, ProxyServer.key)
        except Exception, e:
            raise PolicyStorageError(ProxyServer.error(e))
