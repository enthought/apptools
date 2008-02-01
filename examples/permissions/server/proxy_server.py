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
import os
import socket
import xmlrpclib


# The default IP address to connect to.
DEFAULT_ADDR = socket.gethostbyname(socket.gethostname())

# The default port to connect to.
DEFAULT_PORT = 3800


class ProxyServer(xmlrpclib.ServerProxy):
    """This is a thin wrapper around xmlrpclib.ServerProxy that handles the
    server address and error reporting."""

    def __init__(self):
        """Initialise the object.  The server address and TCP/IP port are taken
        from the ETS_PERMS_SERVER environment variable if set."""

        self._server = os.environ.get('ETS_PERMS_SERVER',
                '%s:%d' % (DEFAULT_ADDR, DEFAULT_PORT))

        xmlrpclib.ServerProxy.__init__(self, uri='http://%s' % self._server)

    def error(self, e):
        """Return a user friendly string describing the given exception."""

        if isinstance(e, socket.error):
            err, msg = e.args

            if err == errno.ECONNREFUSED:
                emsg = "Unable to connect to permissions server at %s." % self._server
            else:
                emsg = "Socket error to permissions server at %s." % self._server
        elif isinstance(e, xmlrpclib.Fault):
            # Extract the text of the exception.  If we don't recognise the
            # format then display the lot.
            tail = e.faultString.find(':')
            if tail < 0:
                emsg = "Unexpected exception from permissions server at %s: %s\n" % (self._server, e.faultString)
            else:
                emsg = e.faultString[tail + 1:]
        else:
            # Let any existing error handling deal with it.
            raise e

        return emsg
