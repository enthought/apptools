#!/usr/bin/env python

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
import logging
import SimpleXMLRPCServer
import socket


# Log to stderr.
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

# The default IP address to listen on.
DEFAULT_ADDR = socket.gethostbyname(socket.gethostname())

# The default port to listen on.
DEFAULT_PORT = 3800


class ServerImplementation(object):
    """This is a container for all the functions implemented by the server."""

    def get_user(self, name):

        if name == 'phil':
            return ('phil', 'Phil Thompson', '', 'foobar')

        return ('', '', '', '')


class RPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer):
    """A thin wrapper around SimpleXMLRPCServer that handles its
    initialisation."""

    def __init__(self, addr=DEFAULT_ADDR, port=DEFAULT_PORT):
        """Initialise the object."""

        SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self, (addr, port))

        self.register_instance(ServerImplementation())


if __name__ == '__main__':

    # Parse the command line.
    import optparse

    p = optparse.OptionParser(description="This is an XML-RPC server that "
            "provides user, role and permissions data to a user and policy "
            "manager that is part of the ETS Permissions Framework.")

    p.add_option('-a', '--ip-address', default=DEFAULT_ADDR, dest='addr',
            help="the IP address to listen on [default: %s]" % DEFAULT_ADDR)
    p.add_option('-p', '--port', type='int', default=DEFAULT_PORT, dest='port',
            help="the TCP port to listen on [default: %d]" % DEFAULT_PORT)

    opts, args = p.parse_args()

    if args:
        p.error("unexpected additional arguments: %s" % " ".join(args))

    # Create and start the server.
    server = RPCServer(addr=opts.addr, port=opts.port)

    logger.info("server starting")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    else:
        raise

    logger.info("server terminated")
