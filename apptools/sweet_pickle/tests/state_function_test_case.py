#-----------------------------------------------------------------------------
#
#  Copyright (c) 2006 by Enthought, Inc.
#  All rights reserved.
#
#  Author: Dave Peterson <dpeterson@enthought.com>
#
#-----------------------------------------------------------------------------

""" Tests the state function functionality of the apptools.sweet_pickle
    framework.
"""

# Standard library imports.
import unittest
import logging

# Enthought library imports
import apptools.sweet_pickle as sweet_pickle
from apptools.sweet_pickle.global_registry import _clear_global_registry
from traits.api import Bool, Float, HasTraits, Int, Str


logger = logging.getLogger(__name__)


##############################################################################
# Classes to use within the tests
##############################################################################

# Need complete package name so that mapping matches correctly.
# The problem here is the Python loader that will load the same module with
# multiple names in sys.modules due to relative naming. Nice.
from apptools.sweet_pickle.tests.state_function_classes import Foo, Bar, Baz

##############################################################################
# State functions to use within the tests
##############################################################################

def bar_state_function(state):
    for old, new in [('b1', 'b2'), ('f1', 'f2'), ('i1', 'i2'), ('s1', 's2')]:
        state[new] = state[old]
        del state[old]
    state['_enthought_pickle_version'] = 2
    return state


##############################################################################
# class 'StateFunctionTestCase'
##############################################################################

class StateFunctionTestCase(unittest.TestCase):
    """ Tests the state function functionality of the apptools.sweet_pickle
        framework.
    """

    ##########################################################################
    # 'TestCase' interface
    ##########################################################################

    ### public interface #####################################################

    def setUp(self):
        """ Creates the test fixture.

            Overridden here to ensure each test starts with an empty global
            registry.
        """
        # Clear the global registry
        _clear_global_registry()

        # Cache a reference to the new global registry
        self.registry = sweet_pickle.get_global_registry()

        # Add the class mappings to the registry
        self.registry.add_mapping_to_class(Foo.__module__, Foo.__name__,
            Bar)
        self.registry.add_mapping_to_class(Bar.__module__, Bar.__name__,
            Baz)


    ##########################################################################
    # 'StateFunctionTestCase' interface
    ##########################################################################

    ### public interface #####################################################

    def test_normal_setstate(self):
        """ Validates that only existing setstate methods are called when
            there are no registered state functions in the class chain.
        """
        # Validate that unpickling the first class gives us an instance of
        # the third class with the appropriate attribute values.  It will have
        # the default Foo values (because there is no state function to move
        # them) and also the default Baz values (since they inherit the
        # trait defaults because nothing overwrote the values.)
        start = Foo()
        end = sweet_pickle.loads(sweet_pickle.dumps(start))
        self.assertEqual(True, isinstance(end, Baz))
        self._assertAttributes(end, 1, (False, 1, 1, 'foo'))
        self._assertAttributes(end, 2, None)
        self._assertAttributes(end, 3, (False, 3, 3, 'baz'))

        # Validate that unpickling the second class gives us an instance of
        # the third class with the appropriate attribute values.  It will have
        # only the Baz attributes with the Bar values (since the __setstate__
        # on Baz converted the Bar attributes to Baz attributes.)
        start = Bar()
        end = sweet_pickle.loads(sweet_pickle.dumps(start))
        self.assertEqual(True, isinstance(end, Baz))
        self._assertAttributes(end, 2, None)
        self._assertAttributes(end, 3, (True, 2, 2, 'bar'))


    def test_unpickled_chain_functionality(self):
        """ Validates that the registered state functions are used when
            unpickling.
        """
        # Add the state function to the registry
        self.registry.add_state_function_for_class(Bar, 2,
            bar_state_function)

        # Validate that unpickling the first class gives us an instance of
        # the third class with the appropriate attribute values.
        start = Foo()
        end = sweet_pickle.loads(sweet_pickle.dumps(start))
        self.assertEqual(True, isinstance(end, Baz))
        self._assertAttributes(end, 1, None)
        self._assertAttributes(end, 2, None)
        self._assertAttributes(end, 3, (False, 1, 1, 'foo'))

        # Validate that unpickling the second class gives us an instance of
        # the third class.
        start = Bar()
        end = sweet_pickle.loads(sweet_pickle.dumps(start))
        self.assertEqual(True, isinstance(end, Baz))
        self._assertAttributes(end, 2, None)
        self._assertAttributes(end, 3, (True, 2, 2, 'bar'))


    ### protected interface ##################################################

    def _assertAttributes(self, obj, suffix, values):
        """ Ensures that the specified object's attributes with the specified
            suffix have the expected values.  If values is None, then the
            attributes shouldn't exist.
        """
        attributeNames = ['b', 'f', 'i', 's']
        for i in range(len(attributeNames)):
            name = attributeNames[i] + str(suffix)
            if values is None:
                self.assertEqual(False, hasattr(obj, name),
                    'Obj [%s] has attribute [%s]' % (obj, name))
            else:
                self.assertEqual(values[i], getattr(obj, name),
                    'Obj [%s] attribute [%s] has [%s] instead of [%s]' % \
                    (obj, name, values[i], getattr(obj, name)))


if __name__ == "__main__":
    unittest.main()


### EOF ######################################################################
