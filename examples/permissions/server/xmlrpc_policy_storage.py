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

    #### Private interface ###################################################

    # The proxy for the XML RPC server.
    _server = Instance(ProxyServer)

    ###########################################################################
    # 'IPolicyStorage' interface.
    ###########################################################################

    def is_empty(self):
        """See if the database is empty."""

        try:
            return self._server.is_empty_policy()
        except Exception, e:
            raise PolicyStorageError(self._server.error(e))

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def __server_default(self):
        """Return the default proxy server."""

        return ProxyServer()
