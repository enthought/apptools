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

# Third-party imports.
import six.moves.cPickle as pickle

# Enthought library imports.
from traits.etsconfig.api import ETSConfig


class Persistent(object):
    """This persists a Traits class to a file.  It is used by the default
    permissions policy and user manager to implement basic (ie.  insecure)
    shared data storage."""

    def __init__(self, factory, file_name, desc):
        """Initialise the object.  factory is a callable that will create a
        new instance if there is no existing data.  file_name is the name of
        the file in the ETSConfig.application_home directory (or the directory
        specified by the ETS_PERMS_DATA_DIR environment variable if set) to
        persist the data to.  desc is a description of the data used in
        exceptions."""

        self._factory = factory
        self._desc = desc

        # Get the name of the file to use.
        data_dir = os.environ.get('ETS_PERMS_DATA_DIR',
                ETSConfig.application_home)
        self._fname = os.path.join(data_dir, file_name)
        self._lock = self._fname + '.lock'

        try:
            os.makedirs(data_dir)
        except OSError:
            pass

    def lock(self):
        """Obtain a lock on the persisted data."""

        try:
            os.mkdir(self._lock)
        except OSError as e:
            if e.errno == errno.EEXIST:
                msg = "The lock on %s is held by another application or user." % self._desc
            else:
                msg = "Unable to acquire lock on %s: %s." % (self._desc, e)

            raise PersistentError(msg)

    def unlock(self):
        """Release the lock on the persisted data."""

        try:
            os.rmdir(self._lock)
        except OSError as e:
            raise PersistentError("Unable to release lock on %s: %s." % (self._desc, e))

    def read(self):
        """Read and return the persisted data."""

        try:
            f = open(self._fname, 'r')

            try:
                try:
                    data = pickle.load(f)
                except:
                    raise PersistentError("Unable to read %s." % self._desc)
            finally:
                f.close()
        except IOError as e:
            if e.errno == errno.ENOENT:
                data = self._factory()
            else:
                raise PersistentError("Unable to open %s: %s." % (self._desc, e))

        return data

    def write(self, data):
        """Write the persisted data."""

        try:
            f = open(self._fname, 'w')

            try:
                try:
                    pickle.dump(data, f)
                except:
                    raise PersistentError("Unable to write %s." % self._desc)
            finally:
                f.close()
        except IOError as e:
            raise PersistentError("Unable to create %s: %s." % (self._desc, e))


class PersistentError(Exception):
    """The class used for all persistence related exceptions."""
