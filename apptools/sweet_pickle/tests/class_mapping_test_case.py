#-----------------------------------------------------------------------------
#
#  Copyright (c) 2006 by Enthought, Inc.
#  All rights reserved.
#
#  Author: Dave Peterson <dpeterson@enthought.com>
#
#-----------------------------------------------------------------------------

""" Tests the class mapping functionality of the enthought.pickle
    framework.
"""

# Standard library imports.
import unittest

# Enthought library imports
import apptools.sweet_pickle as sweet_pickle
from apptools.sweet_pickle.global_registry import _clear_global_registry


##############################################################################
# Classes to use within the tests
##############################################################################

# Need complete package name so that mapping matches correctly.
# The problem here is the Python loader that will load the same module with
# multiple names in sys.modules due to relative naming. Nice.
from apptools.sweet_pickle.tests.class_mapping_classes import Foo, Bar, Baz

##############################################################################
# class 'ClassMappingTestCase'
##############################################################################

class ClassMappingTestCase(unittest.TestCase):
    """ Tests the class mapping functionality of the apptools.sweet_pickle
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


    ##########################################################################
    # 'ClassMappingTestCase' interface
    ##########################################################################

    ### public interface #####################################################

    def test_infinite_loop_detection(self):
        """ Validates that the class mapping framework detects infinite
            loops of class mappings.
        """
        # Add mappings to the registry
        self.registry.add_mapping_to_class(Foo.__module__, Foo.__name__, Bar)
        self.registry.add_mapping_to_class(Bar.__module__, Bar.__name__, Baz)
        self.registry.add_mapping_to_class(Baz.__module__, Baz.__name__, Foo)

        # Validate that an exception is raised when trying to unpickle an
        # instance anywhere within the circular definition.
        def fn(o):
            sweet_pickle.loads(sweet_pickle.dumps(o))
        self.assertRaises(sweet_pickle.UnpicklingError, fn, Foo())
        self.assertRaises(sweet_pickle.UnpicklingError, fn, Bar())
        self.assertRaises(sweet_pickle.UnpicklingError, fn, Baz())


    def test_unpickled_class_mapping(self):

        # Add the mappings to the registry
        self.registry.add_mapping_to_class(Foo.__module__, Foo.__name__, Bar)
        self.registry.add_mapping_to_class(Bar.__module__, Bar.__name__, Baz)

        # Validate that unpickling the first class gives us an instance of
        # the third class.
        start = Foo()
        end = sweet_pickle.loads(sweet_pickle.dumps(start))
        self.assertEqual(True, isinstance(end, Baz))

        # Validate that unpickling the second class gives us an instance of
        # the third class.
        start = Bar()
        end = sweet_pickle.loads(sweet_pickle.dumps(start))
        self.assertEqual(True, isinstance(end, Baz))


if __name__ == "__main__":
    unittest.main()


### EOF ######################################################################
