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

    def __init__(self, data_dir, insecure, local_user_db):
        """Initialise the object."""

        self._data_dir = data_dir
        self._insecure = insecure
        self._local_user_db = local_user_db

        # Make sure we can call _close() at any time.
        self._roles = self._assignments = self._blobs = self._users = None

        # Make sure the data directory exists.
        if not os.path.isdir(self._data_dir):
            os.mkdir(self._data_dir)

        # Load the data.
        self._roles = self._open_shelf('roles')
        self._assignments = self._open_shelf('assignments')
        self._blobs = self._open_shelf('blobs')

        if self._local_user_db:
            self._users = self._open_shelf('users')

    def _close(self):
        """Close all the databases."""

        if self._roles is not None:
            self._roles.close()
            self._roles = None

        if self._assignments is not None:
            self._assignments.close()
            self._assignments = None

        if self._blobs is not None:
            self._blobs.close()
            self._blobs = None

        if self._users is not None:
            if self._local_user_db:
                self._users.close()

            self._users = None

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

    def capabilities(self):
        """Return a list of capabilities that the implementation supports.  The
        full list is 'user_password', 'user_add', 'user_modify', 'user_delete'.
        """

        caps = ['user_password']

        if self._local_user_db:
            # FIXME
            #caps.extend(['user_add', 'user_modify', 'user_delete'])
            caps.extend(['user_add'])

        return caps

    def add_user(self, name, description, password, key=None):
        """Add a new user."""

        self._check_authorisation(key)

        if self._local_user_db:
            if self._users.has_key(name):
                raise Exception("The user \"%s\" already exists." % name)

            self._users[name] = (description, password)
            self._sync(self._users)
        else:
            raise Exception("Adding a user isn't supported.")

        return True

    def get_user(self, name, key=None):
        """Return the tuple of the user name, description, blob and password.
        """

        self._check_authorisation(key)

        if self._local_user_db:
            try:
                description, password = self._users[name]
            except KeyError:
                name = description = password = ''
        else:
            # FIXME
            raise Exception("Getting a user isn't yet supported.")

        # Get the blob if there is one.
        try:
            blob = self._blobs[name]
        except KeyError:
            blob = ''

        return (name, description, blob, password)

    def add_role(self, name, description, perm_names, key=None):
        """Add a new role."""

        self._check_authorisation(key)

        if self._roles.has_key(name):
            raise Exception("The role \"%s\" already exists." % name)

        self._roles[name] = (description, perm_names)
        self._sync(self._roles)

        # Return a non-None value.
        return True

    def all_roles(self, key=None):
        """Return a list of all roles."""

        self._check_authorisation(key)

        return [(name, description)
                for name, (description, _) in self._roles.items()]

    def delete_role(self, name, key=None):
        """Delete a role."""

        self._check_authorisation(key)

        if not self._roles.has_key(name):
            raise Exception("The role \"%s\" does not exist." % name)

        del self._roles[name]

        # Remove the role from any users who have it.
        for user, role_names in self._assignments.items():
            try:
                role_names.remove(name)
            except ValueError:
                continue

            self._assignments[user] = role_names

        self._sync(self._roles)
        self._sync(self._assignments)

        # Return a non-None value.
        return True

    def get_assignment(self, user_name, key=None):
        """Return the details of the assignment for the given user name."""

        self._check_authorisation(key)

        try:
            role_names = self._assignments[user_name]
        except KeyError:
            return '', []

        return user_name, role_names

    def get_policy(self, user_name, key=None):
        """Return the details of the policy for the given user name."""

        self._check_authorisation(key)

        try:
            role_names = self._assignments[user_name]
        except KeyError:
            return '', []

        perm_names = []

        for r in role_names:
            _, perms = self._roles[r]
            perm_names.extend(perms)

        return user_name, perm_names

    def get_roles(self, name, key=None):
        """Return the full name, description and permissions of all the roles
        that match the given name."""

        self._check_authorisation(key)

        # Return any role that starts with the name.
        return [(full_name, description, perm_names)
                for full_name, (description, perm_names) in self._roles.items()
                        if full_name.startswith(name)]

    def is_empty_policy(self):
        """Return True if there is no useful data."""

        empty = (len(self._roles) == 0 or len(self._assignments) == 0)

        # Include the users as well if the database is local.
        if self._local_user_db and len(self._users) == 0:
            empty = True

        return empty

    def save_assignment(self, user_name, role_names, key=None):
        """Save the roles assigned to a user."""

        self._check_authorisation(key)

        if len(role_names) == 0:
            # Delete the user, but don't worry if there is no current
            # assignment.
            try:
                del self._assignments[user_name]
            except KeyError:
                pass
        else:
            self._assignments[user_name] = role_names

        self._sync(self._assignments)

        # Return a non-None value.
        return True

    def update_role(self, name, description, perm_names, key=None):
        """Update an existing role."""

        self._check_authorisation(key)

        if not self._roles.has_key(name):
            raise Exception("The role \"%s\" does not exist." % name)

        self._roles[name] = (description, perm_names)
        self._sync(self._roles)

        # Return a non-None value.
        return True


class RPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer):
    """A thin wrapper around SimpleXMLRPCServer that handles its
    initialisation."""

    def __init__(self, addr=DEFAULT_ADDR, port=DEFAULT_PORT,
            data_dir=DEFAULT_DATADIR, insecure=False, local_user_db=False):
        """Initialise the object."""

        SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self, (addr, port))

        self._impl = ServerImplementation(data_dir, insecure, local_user_db)
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

    p.add_option('--data-dir', default=DEFAULT_DATADIR, dest='data_dir',
            metavar="DIR",
            help="the server's data directory [default: %s]" % DEFAULT_DATADIR)
    p.add_option('--insecure', action='store_true', default=False,
            dest='insecure',
            help="don't require a session key for data changes")
    p.add_option('--ip-address', default=DEFAULT_ADDR, dest='addr',
            help="the IP address to listen on [default: %s]" % DEFAULT_ADDR)
    p.add_option('--local-user-db', action='store_true', default=False,
            dest='local_user_db',
            help="use a local user database instead of an LDAP directory")
    p.add_option('--port', type='int', default=DEFAULT_PORT, dest='port',
            help="the TCP port to listen on [default: %d]" % DEFAULT_PORT)

    opts, args = p.parse_args()

    if args:
        p.error("unexpected additional arguments: %s" % " ".join(args))

    # FIXME: Add LDAP support.
    if not opts.local_user_db:
        sys.stderr.write("Until LDAP support is implemented use the --local-user-db flag\n")
        sys.exit(1)

    # Create and start the server.
    server = RPCServer(addr=opts.addr, port=opts.port, data_dir=opts.data_dir,
            insecure=opts.insecure, local_user_db=opts.local_user_db)

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
