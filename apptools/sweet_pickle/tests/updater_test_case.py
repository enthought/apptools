#-----------------------------------------------------------------------------
#
#  Copyright (c) 2006 by Enthought, Inc.
#  All rights reserved.
#
#  Author: Dave Peterson <dpeterson@enthought.com>
#
#-----------------------------------------------------------------------------

""" Tests the updater functionality of the sweet_pickle framework.
"""

# Standard library imports.
import unittest
import logging

# Enthought library imports
import apptools.sweet_pickle as sweet_pickle
from apptools.sweet_pickle.global_registry import _clear_global_registry


logger = logging.getLogger(__name__)


##############################################################################
# class 'UpdaterTestCase'
##############################################################################

class UpdaterTestCase(unittest.TestCase):
    """ Tests the updater functionality of the sweet_pickle framework.
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
    # 'UpdaterTestCase' interface
    ##########################################################################

    ### public interface #####################################################

    def test_add_mapping(self):
        """ Validates the behavior of the add_mapping function.
        """
        # Add a single mapping and validate that all it did was add a class
        # mapping and that the mapping has the expected values.
        key = ('foo', 'Foo')
        value = ('bar', 'Bar')
        self.registry.add_mapping(key[0], key[1], value[0], value[1])
        self._validate_exactly_one_class_map(key, value)

        # Overwrite with a new mapping and validate the state is what we
        # expect.
        value = ('baz', 'Baz')
        self.registry.add_mapping(key[0], key[1], value[0], value[1])
        self._validate_exactly_one_class_map(key, value)


    def test_add_mapping_to_class(self):
        """ Validates the behavior of the add_mapping_to_class function.
        """
        # Add a single mapping and validate that all it did was add a class
        # mapping and that the mapping has the expected values.
        key = ('foo', 'Foo')
        class Bar:
            pass
        value = (Bar.__module__, 'Bar')
        self.registry.add_mapping_to_class(key[0], key[1], Bar)
        self._validate_exactly_one_class_map(key, value)

        # Overwrite with a new mapping and validate the state is what we
        # expect.
        class Baz:
            pass
        value = (Baz.__module__, 'Baz')
        self.registry.add_mapping_to_class(key[0], key[1], Baz)
        self._validate_exactly_one_class_map(key, value)


    def test_add_mappings(self):
        """ Validates the behavior of the add_mappings function.
        """
        # Add a single mapping and validate that all it did was add a class
        # mapping and that the mapping has the expected values
        key = ('foo', 'Foo')
        value = ('bar', key[1])
        names = [key[1]]
        self.registry.add_mappings(key[0], value[0], names)
        self._validate_exactly_one_class_map(key, value)

        # Add multiple mappings and validate that the registry has the expected
        # values.
        key = ('foo', 'Foo')
        value = ('bar', 'Bar')
        names = ['Foo', 'Bar', 'Baz', 'Enthought']
        self.registry.add_mappings(key[0], value[0], names)
        self.assertEqual(len(names), len(self.registry.class_map))
        self.assertEqual(0, len(self.registry.state_functions))
        self.assertEqual(0, len(self.registry.version_attribute_map))
        self.assertEqual(0, len(self.registry._state_function_classes))
        items = []
        for n in names:
            items.append( ((key[0], n), (value[0], n)) )
        self._validate_class_map_contents(items)


    def test_add_state_function(self):
        """ Validates the behavior of the add_state_function function.
        """
        # Add a single function and validate that all it did was add a state
        # mapping and that the mapping has the expected values.
        key = ('foo', 'Foo', 1)
        def fn():
            pass
        self.registry.add_state_function(key[0], key[1], key[2], fn)
        self._validate_exactly_one_state_function(key, [fn])

        # Add an additional function for the same state and validate the state
        # is what we expect.
        def fn2():
            pass
        self.registry.add_state_function(key[0], key[1], key[2], fn2)
        self._validate_exactly_one_state_function(key, [fn, fn2])

        # Add a state function for another version of the same class and
        # validate that all the values are as expected.
        key2 = ('foo', 'Foo', 2)
        self.registry.add_state_function(key2[0], key2[1], key2[2], fn2)
        self.assertEqual(0, len(self.registry.class_map))
        self.assertEqual(2, len(self.registry.state_functions))
        self.assertEqual(0, len(self.registry.version_attribute_map))
        self.assertEqual(1, len(self.registry._state_function_classes))
        self._validate_state_function_contents(
            [(key, [fn, fn2]), (key2, [fn2])],
            {(key[0], key[1]): 3}
            )


    def test_add_state_function_for_class(self):
        """ Validates the behavior of the add_state_function_for_class function.
        """
        # Add a single function and validate that all it did was add a state
        # mapping and that the mapping has the expected values.
        class Bar:
            pass
        key = (Bar.__module__, 'Bar', 1)
        def fn():
            pass
        self.registry.add_state_function_for_class(Bar, key[2], fn)
        self._validate_exactly_one_state_function(key, [fn])

        # Add an additional function for the same state and validate the state
        # is what we expect.
        def fn2():
            pass
        self.registry.add_state_function_for_class(Bar, key[2], fn2)
        self._validate_exactly_one_state_function(key, [fn, fn2])

        # Add a state function for another class and validate that all the
        # values are as expected.
        class Baz:
            pass
        key2 = (Baz.__module__, 'Baz', 2)
        self.registry.add_state_function_for_class(Baz, key2[2], fn2)
        self.assertEqual(0, len(self.registry.class_map))
        self.assertEqual(2, len(self.registry.state_functions))
        self.assertEqual(0, len(self.registry.version_attribute_map))
        self.assertEqual(2, len(self.registry._state_function_classes))
        self._validate_state_function_contents(
            [(key, [fn, fn2]), (key2, [fn2])],
            {(key[0], key[1]): 2, (key2[0], key2[1]): 1}
            )


    def test_merge_updater(self):
        """ Validates the behavior of the merge_updater function.
        """
        # Merge in one update and validate the state of the registry is as
        # expected.
        def fn1():
            pass
        updater = sweet_pickle.Updater(
            class_map = {
                ('foo', 'Foo'): ('foo.bar', 'Foo'),
                },
            state_functions = {
                ('foo', 'Foo', 1): [fn1],
                },
            version_attribute_map = {
                ('foo', 'Foo'): 'version',
                },
            )
        self.registry.merge_updater(updater)
        self.assertEqual(1, len(self.registry.class_map))
        self.assertEqual(1, len(self.registry.state_functions))
        self.assertEqual(1, len(self.registry.version_attribute_map))
        self.assertEqual(1, len(self.registry._state_function_classes))
        self._validate_class_map_contents(list(updater.class_map.items()))
        counts = {('foo', 'Foo'): 1}
        self._validate_state_function_contents(list(updater.state_functions.items()),
            counts)

        # Merge in a second updater and validate the state of the registry is
        # as expected.
        def fn2():
            pass
        updater2 = sweet_pickle.Updater(
            class_map = {
                ('foo.bar', 'Foo'): ('bar', 'Bar'),
                ('bar', 'Bar'): ('foo.bar.baz', 'Baz'),
                },
            state_functions = {
                ('foo', 'Foo', 1): [fn2],
                ('foo', 'Foo', 2): [fn2],
                },
            version_attribute_map = {
                ('foo.bar', 'Foo'): '_version',
                },
            )
        self.registry.merge_updater(updater2)
        self.assertEqual(3, len(self.registry.class_map))
        self.assertEqual(2, len(self.registry.state_functions))
        self.assertEqual(2, len(self.registry.version_attribute_map))
        self.assertEqual(1, len(self.registry._state_function_classes))
        self._validate_class_map_contents(
            list(updater.class_map.items()) + list(updater2.class_map.items())
        )
        counts = {('foo', 'Foo'): 3}
        self._validate_state_function_contents(
            [ (('foo', 'Foo', 1), [fn1, fn2]), (('foo', 'Foo', 2), [fn2]) ],
            counts)


    def test_registry_starts_empty(self):
        """ Validates that the registry is starting empty for each test.
        """
        self.assertEqual(0, len(self.registry.class_map))
        self.assertEqual(0, len(self.registry.state_functions))
        self.assertEqual(0, len(self.registry.version_attribute_map))
        self.assertEqual(0, len(self.registry._state_function_classes))


    ### protected interface ##################################################

    def _validate_class_map_contents(self, items):
        """ Validates that the registry's class_map contains the specified
            items.
        """
        for key, value in items:
            self.assertEqual(True, key in self.registry.class_map,
                'Key ' + str(key) + ' not in class_map')
            self.assertEqual(value, self.registry.class_map[key],
                str(value) + ' != ' + str(self.registry.class_map[key]) + \
                ' for key ' + str(key))
            self.assertEqual(True,
                self.registry.has_class_mapping(key[0], key[1]),
                'Registry reports no class mapping for key ' + str(key))


    def _validate_exactly_one_class_map(self, key, value):
        """ Validates that the registry has exactly one class_map entry
            with the specified key and value.
        """
        self.assertEqual(1, len(self.registry.class_map))
        self.assertEqual(0, len(self.registry.state_functions))
        self.assertEqual(0, len(self.registry.version_attribute_map))
        self.assertEqual(0, len(self.registry._state_function_classes))
        self._validate_class_map_contents([(key, value)])


    def _validate_exactly_one_state_function(self, key, value):
        """ Validates that the registry has exactly one state_function entry
            with the specified key and value.
        """
        self.assertEqual(0, len(self.registry.class_map))
        self.assertEqual(1, len(self.registry.state_functions))
        self.assertEqual(0, len(self.registry.version_attribute_map))
        self.assertEqual(1, len(self.registry._state_function_classes))
        self.assertEqual(key, list(self.registry.state_functions.keys())[0])
        self.assertEqual(value, self.registry.state_functions[key])
        classes_key = (key[0], key[1])
        self.assertEqual(classes_key,
            list(self.registry._state_function_classes.keys())[0])
        self.assertEqual(len(value),
            self.registry._state_function_classes[classes_key])


    def _validate_state_function_contents(self, items, counts):
        """ Validates that the registry's state functions contains the
            specified items and the class count matches the specified count.
        """
        for key, value in items:
            self.assertEqual(True, key in self.registry.state_functions,
                'Key ' + str(key) + ' not in state functions')
            self.assertEqual(value, self.registry.state_functions[key],
                str(value) + ' != ' + \
                str(self.registry.state_functions[key]) + ' for key ' + \
                str(key))
            self.assertEqual(True, self.registry.has_state_function(
                key[0], key[1]),
                'Registry reports no state function for key ' + str(key))

            classes_key = (key[0], key[1])
            count = counts[classes_key]
            self.assertEqual(count,
                self.registry._state_function_classes[classes_key])


if __name__ == "__main__":
    unittest.main()


### EOF ######################################################################
