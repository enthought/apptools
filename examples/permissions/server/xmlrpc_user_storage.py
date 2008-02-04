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


class XMLRPCUserStorage(HasTraits):
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

    def is_empty(self):
        """See if the database is empty."""

        # We leave it to the policy storage to answer this question.
        return False

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
