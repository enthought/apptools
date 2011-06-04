#-----------------------------------------------------------------------------
#
#  Copyright (c) 2006 by Enthought, Inc.
#  All rights reserved.
#
#  Author: Dave Peterson <dpeterson@enthought.com>
#
#-----------------------------------------------------------------------------

""" Tests the global registry functionality of the sweet_pickle framework.
"""

# Standard library imports.
import unittest

# Enthought library imports
import apptools.sweet_pickle as sweet_pickle
from apptools.sweet_pickle.global_registry import _clear_global_registry


##############################################################################
# class 'GlobalRegistryTestCase'
##############################################################################

class GlobalRegistryTestCase(unittest.TestCase):
    """ Tests the global registry functionality of the sweet_pickle framework.
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
    # 'GlobalRegistryTestCase' interface
    ##########################################################################

    ### public interface #####################################################

    def test_clearing(self):
        """ Validates that clearing the registry gives us a new registry.
        """
        _clear_global_registry()
        self.assertNotEqual(self.registry, sweet_pickle.get_global_registry())


    def test_registry_starts_empty(self):
        """ Validates that the registry is starting empty for each test.
        """
        self.assertEqual(0, len(self.registry.class_map))
        self.assertEqual(0, len(self.registry.state_functions))
        self.assertEqual(0, len(self.registry.version_attribute_map))
        self.assertEqual(0, len(self.registry._state_function_classes))


    def test_returns_singleton(self):
        """ Validates that the getter returns the same global registry
        """
        # Just try it a few times.
        self.assertEqual(self.registry, sweet_pickle.get_global_registry())
        self.assertEqual(self.registry, sweet_pickle.get_global_registry())
        self.assertEqual(self.registry, sweet_pickle.get_global_registry())


if __name__ == "__main__":
    unittest.main()


### EOF ######################################################################
