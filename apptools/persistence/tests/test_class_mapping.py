# -----------------------------------------------------------------------------
#
#  Copyright (c) 2006 by Enthought, Inc.
#  All rights reserved.
#
#  Author: Dave Peterson <dpeterson@enthought.com>
#
# -----------------------------------------------------------------------------

""" Tests the class mapping functionality of the enthought.pickle
    framework.
"""

# Standard library imports.
import io
import pickle
import unittest

# Enthought library imports
from apptools.persistence.versioned_unpickler import VersionedUnpickler
from apptools.persistence.updater import Updater


##############################################################################
# Classes to use within the tests
##############################################################################


class Foo:
    pass


class Bar:
    pass


class Baz:
    pass


##############################################################################
# class 'ClassMappingTestCase'
##############################################################################


class ClassMappingTestCase(unittest.TestCase):
    """Tests the class mapping functionality of the apptools.sweet_pickle
    framework.
    """

    ##########################################################################
    # 'TestCase' interface
    ##########################################################################

    ### public interface #####################################################

    def test_unpickled_class_mapping(self):

        class TestUpdater(Updater):
            def __init__(self):
                self.refactorings = {
                    (Foo.__module__, Foo.__name__): (Bar.__module__, Bar.__name__),
                    (Bar.__module__, Bar.__name__): (Baz.__module__, Baz.__name__),
                }
                self.setstates = {}

        # Validate that unpickling the first class gives us an instance of
        # the second class.
        start = Foo()
        test_file = io.BytesIO(pickle.dumps(start, 2))
        end = VersionedUnpickler(test_file, updater=TestUpdater()).load()
        self.assertIsInstance(end, Bar)

        # Validate that unpickling the second class gives us an instance of
        # the third class.
        start = Bar()
        test_file = io.BytesIO(pickle.dumps(start, 2))
        end = VersionedUnpickler(test_file, updater=TestUpdater()).load()
        self.assertIsInstance(end, Baz)
