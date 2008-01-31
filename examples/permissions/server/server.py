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
import errno
import logging
import os
import shelve
import SimpleXMLRPCServer
import socket
import sys


# Log to stderr.
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

# The default IP address to listen on.
DEFAULT_ADDR = socket.gethostbyname(socket.gethostname())

# The default port to listen on.
DEFAULT_PORT = 3800

# The default data directory.
DEFAULT_DATADIR = os.path.expanduser('~/.ets_perms_server')


class ServerImplementation(object):
    """This is a container for all the functions implemented by the server."""

    def __init__(self, data_dir, insecure):
        """Initialise the object."""

        self._data_dir = data_dir
        self._insecure = insecure

        # Make sure we can call _close() at any time.
        self._roles = self._assignments = None

        # Make sure the data directory exists.
        if not os.path.isdir(self._data_dir):
            os.mkdir(self._data_dir)

        # Load the data.
        self._roles = self._open_shelf('roles')
        self._assignments = self._open_shelf('assignments')

    def _close(self):
        """Close all the databases."""

        if self._roles is not None:
            self._roles.close()
            self._roles = None

        if self._assignments is not None:
            self._assignments.close()
            self._assignments = None

    def _open_shelf(self, name):
        """Open a shelf."""

        logger.info("Loading %s" % name)

        fname = os.path.join(self._data_dir, name)

        try:
            return shelve.open(fname, writeback=True)
        except Exception, e:
            logger.error("Unable to open %s: %s" % (fname, e))
            sys.exit(1)

    @staticmethod
    def _sync(shelf):
        try:
            shelf.sync()
        except Exception, e:
            logger.error("Unable to sync:" % e)
            Exception("An error occurred on the permissions server.")

    def _check_authorisation(self, key):
        """Check that the action is authorised, either because the user
        associated with the key has the appropriate permission, or we are
        running in insecure mode, or we are bootstrapping."""

        # Handle the easy cases first.
        if self._insecure or self.is_empty_policy():
            return

        # FIXME: Check the key and the user permissions.
        raise Exception("You do not have the appropriate authority.")

    def add_role(self, name, description, perm_names, key=None):
        """Add a new role."""

        self._check_authorisation(key)

        if self._roles.has_key(name):
            raise Exception("The role \"%s\" already exists." % name)

        self._roles[name] = (description, perm_names)
        self._sync(self._roles)

        return True

    def add_user(self, name, description, password, key=None):

        raise Exception("add_user not yet implemented")

        return True

    def get_user(self, name):

        if name == 'phil':
            return ('phil', 'Phil Thompson', '', 'foobar')

        raise Exception("The user \"%s\" doesn't exist." % name)

    def is_empty_policy(self):
        """Return True if there is no policy data."""

        return (len(self._roles) == 0 or len(self._assignments) == 0)


class RPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer):
    """A thin wrapper around SimpleXMLRPCServer that handles its
    initialisation."""

    def __init__(self, addr=DEFAULT_ADDR, port=DEFAULT_PORT,
            data_dir=DEFAULT_DATADIR, insecure=False):
        """Initialise the object."""

        SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self, (addr, port))

        self._impl = ServerImplementation(data_dir, insecure)
        self.register_instance(self._impl)

    def server_close(self):
        """Reimplemented to tidy up the implementation."""

        SimpleXMLRPCServer.SimpleXMLRPCServer.server_close(self)

        self._impl._close()


if __name__ == '__main__':

    # Parse the command line.
    import optparse

    p = optparse.OptionParser(description="This is an XML-RPC server that "
            "provides user, role and permissions data to a user and policy "
            "manager that is part of the ETS Permissions Framework.")

    p.add_option('--insecure', action='store_true', default=False,
            dest='insecure',
            help="don't require a session key for data changes")
    p.add_option('--ip-address', default=DEFAULT_ADDR, dest='addr',
            help="the IP address to listen on [default: %s]" % DEFAULT_ADDR)
    p.add_option('--data-dir', default=DEFAULT_DATADIR, dest='data_dir',
            metavar="DIR",
            help="the server's data directory [default: %s]" % DEFAULT_DATADIR)
    p.add_option('--port', type='int', default=DEFAULT_PORT, dest='port',
            help="the TCP port to listen on [default: %d]" % DEFAULT_PORT)

    opts, args = p.parse_args()

    if args:
        p.error("unexpected additional arguments: %s" % " ".join(args))

    # Create and start the server.
    server = RPCServer(addr=opts.addr, port=opts.port, data_dir=opts.data_dir,
            insecure=opts.insecure)

    if opts.insecure:
        logger.warn("Server starting in insecure mode")
    else:
        logger.info("Server starting")

    try:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        else:
            raise
    finally:
        server.server_close()

    logger.info("Server terminated")
