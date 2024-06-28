# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" The base class for all object serializers. """


# Standard library imports.
import logging
from traceback import print_exc
from os.path import splitext
import pickle

# Enthought library imports.
from apptools.persistence.versioned_unpickler import VersionedUnpickler
from traits.api import HasTraits, Str


# Setup a logger for this module.
logger = logging.getLogger(__name__)


class ObjectSerializer(HasTraits):
    """ The base class for all object serializers. """

    #### 'ObjectSerializer' interface #########################################

    # The file extension recognized by this serializer.
    ext = Str(".pickle")

    ###########################################################################
    # 'ObjectSerializer' interface.
    ###########################################################################

    def can_load(self, path):
        """ Returns True if the serializer can load a file. """

        rest, ext = splitext(path)

        return ext == self.ext

    def load(self, path):
        """ Loads an object from a file. """

        # Unpickle the object.
        f = open(path, "rb")
        try:
            try:
                obj = VersionedUnpickler(f).load()
            except Exception as ex:
                print_exc()
                logger.exception(
                    "Failed to load pickle file: %s, %s" % (path, ex)
                )

                raise
        finally:
            f.close()

        return obj

    def can_save(self, obj):
        """ Returns True if the serializer can save an object. """

        return True

    def save(self, path, obj):
        """ Saves an object to a file. """

        if not path.endswith(self.ext):
            actual_path = path + self.ext

        else:
            actual_path = path

        # Pickle the object.
        f = open(actual_path, "wb")
        try:
            pickle.dump(obj, f, 1)
        except Exception as ex:
            logger.exception(
                "Failed to pickle into file: %s, %s, object:%s"
                % (path, ex, obj)
            )
            print_exc()
        f.close()

        return actual_path
