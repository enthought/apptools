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
import cPickle as pickle
import errno
import os
import socket
import xmlrpclib

# Enthought library imports.
from enthought.etsconfig.api import ETSConfig
from enthought.pyface.api import confirm, YES


# The default IP address to connect to.
DEFAULT_ADDR = socket.gethostbyname(socket.gethostname())

# The default port to connect to.
DEFAULT_PORT = 3800


class ProxyServer(xmlrpclib.ServerProxy):
    """This is a thin wrapper around xmlrpclib.ServerProxy that handles the
    server address and error reporting."""

    # The name of the user data cache file.
    _cache_file = os.path.join(ETSConfig.application_home,
            'ets_perms_user_cache')

    def __init__(self):
        """Initialise the object.  The server address and TCP/IP port are taken
        from the ETS_PERMS_SERVER environment variable if set."""

        self._server = os.environ.get('ETS_PERMS_SERVER',
                '%s:%d' % (DEFAULT_ADDR, DEFAULT_PORT))

        xmlrpclib.ServerProxy.__init__(self, uri='http://%s' % self._server)

        # The session key.  It is an empty string if the user is not
        # authenticated and None if the user is in "disconnected" mode.
        self.key = ''

        # The user data cache.  This is a tuple of the user description, blob
        # and list of permission ids when the session key is not an empty
        # string.
        self.cache = None

    def write_cache(self):
        """Write the user cache to persistent storage."""

        f = open(self._cache_file, 'w')
        pickle.dump(self.cache, f)
        f.close()

    def read_cache(self):
        """Read the user cache from persistent storage.  Returns False if
        there was no cache to read."""

        try:
            f = open(self._cache_file, 'r')

            try:
                if confirm(None, "It was not possible to connect to the "
                        "permissions server. Instead you can use the settings "
                        "used when you last logged in from this system. If "
                        "you do this then any changes made to settings "
                        "normally held on the permissions server will be lost "
                        "when you next login successfully.\n\nDo you want to "
                        "use the saved settings?") != YES:
                    raise Exception("")

                try:
                    self.cache = pickle.load(f)
                except:
                    raise Exception("Unable to read %s." % self._cache_file)
            finally:
                f.close()
        except IOError, e:
            if e.errno == errno.ENOENT:
                # There is no cache file.
                return False

            raise Exception("Unable to open %s: %s." % (self._cache_file, e))

        return True

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


# Create a singleton.
ProxyServer = ProxyServer()
