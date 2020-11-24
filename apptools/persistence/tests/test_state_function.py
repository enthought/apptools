# -----------------------------------------------------------------------------
#
#  Copyright (c) 2006 by Enthought, Inc.
#  All rights reserved.
#
#  Author: Dave Peterson <dpeterson@enthought.com>
#
# -----------------------------------------------------------------------------

""" These tests were originally for the the state function functionality of the
now deleted apptools.sweet_pickle framework.  They have been modified here to
use apptools.persistence instead.
"""

# Standard library imports.
import io
import pickle
import unittest
import logging

# Enthought library imports
from apptools.persistence.tests.state_function_classes import Foo, Bar, Baz
from apptools.persistence.versioned_unpickler import VersionedUnpickler
from apptools.persistence.updater import Updater


logger = logging.getLogger(__name__)


def bar_state_function(self, state):
    for old, new in [("b1", "b2"), ("f1", "f2"), ("i1", "i2"), ("s1", "s2")]:
        state[new] = state[old]
        del state[old]
    state["_enthought_pickle_version"] = 2
    return state


class TestUpdater(Updater):
    def __init__(self):
        self.refactorings = {
            (Foo.__module__, Foo.__name__):
                (Bar.__module__, Bar.__name__),
            (Bar.__module__, Bar.__name__):
                (Baz.__module__, Baz.__name__),
        }
        self.setstates = {}


##############################################################################
# class 'StateFunctionTestCase'
##############################################################################


class StateFunctionTestCase(unittest.TestCase):
    """Tests the state function functionality of the apptools.sweet_pickle
    framework.
    """

    ##########################################################################
    # 'TestCase' interface
    ##########################################################################

    ### public interface #####################################################

    def setUp(self):
        """Creates the test fixture.

        Overridden here to ensure each test starts with an empty global
        registry.
        """

        self.updater = TestUpdater()

    ##########################################################################
    # 'StateFunctionTestCase' interface
    ##########################################################################

    ### public interface #####################################################

    def test_normal_setstate(self):
        """Validates that only existing setstate methods are called when
        there are no registered state functions in the class chain.
        """
        # Validate that unpickling the first class gives us an instance of
        # the second class with the appropriate attribute values.  It will have
        # the default Foo values (because there is no state function to move
        # them) and also the default Bar values (since they inherit the
        # trait defaults because nothing overwrote the values.)
        start = Foo()
        test_file = io.BytesIO(pickle.dumps(start, 2))
        end = VersionedUnpickler(test_file, updater=TestUpdater()).load()
        self.assertIsInstance(end, Bar)
        self._assertAttributes(end, 1, (False, 1, 1, "foo"))
        self._assertAttributes(end, 2, (True, 2, 2, "bar"))
        self._assertAttributes(end, 3, None)

        # Validate that unpickling the second class gives us an instance of
        # the third class with the appropriate attribute values.  It will have
        # only the Baz attributes with the Bar values (since the __setstate__
        # on Baz converted the Bar attributes to Baz attributes.)
        start = Bar()
        test_file = io.BytesIO(pickle.dumps(start, 2))
        end = VersionedUnpickler(test_file, updater=TestUpdater()).load()
        self.assertIsInstance(end, Baz)
        self._assertAttributes(end, 2, None)
        self._assertAttributes(end, 3, (True, 2, 2, "bar"))

    ### protected interface ##################################################

    def _assertAttributes(self, obj, suffix, values):
        """Ensures that the specified object's attributes with the specified
        suffix have the expected values.  If values is None, then the
        attributes shouldn't exist.
        """
        attributeNames = ["b", "f", "i", "s"]
        for i in range(len(attributeNames)):
            name = attributeNames[i] + str(suffix)
            if values is None:
                self.assertEqual(
                    False,
                    hasattr(obj, name),
                    "Obj [%s] has attribute [%s]" % (obj, name),
                )
            else:
                self.assertEqual(
                    values[i],
                    getattr(obj, name),
                    "Obj [%s] attribute [%s] has [%s] instead of [%s]"
                    % (obj, name, values[i], getattr(obj, name)),
                )
