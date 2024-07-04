# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Tests for preferences nodes. """


# Standard library imports.
import os
import tempfile
import unittest
from os.path import join

# Major package imports.
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

# Enthought library imports.
from apptools._testing.optional_dependencies import requires_configobj
from apptools.preferences.api import Preferences


# This module's package.
PKG = "apptools.preferences.tests"


@requires_configobj
class PreferencesTestCase(unittest.TestCase):
    """ Tests for preferences nodes. """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        self.preferences = Preferences()

        # The filename of the example preferences file.
        self.example = os.fspath(files(PKG) / "example.ini")

        # A temporary directory that can safely be written to.
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        """ Called immediately after each test method has been called. """

        # Remove the temporary directory.
        os.rmdir(self.tmpdir)

    ###########################################################################
    # Tests.
    ###########################################################################

    def test_package_global_default_preferences(self):
        """ package global default preferences """

        from apptools.preferences.api import get_default_preferences
        from apptools.preferences.api import set_default_preferences

        set_default_preferences(self.preferences)
        self.assertEqual(self.preferences, get_default_preferences())

    def test_get_and_set_str(self):
        """ get and set str """

        p = self.preferences

        # Set a string preference.
        p.set("acme.ui.bgcolor", "blue")
        self.assertEqual("blue", p.get("acme.ui.bgcolor"))

    def test_get_and_set_int(self):
        """ get and set int """

        p = self.preferences

        # Note that we can pass an actual 'int' to 'set', but the preference
        # manager *always* returns preference values as strings.
        p.set("acme.ui.width", 50)
        self.assertEqual("50", p.get("acme.ui.width"))

    def test_get_and_set_float(self):
        """ get and set float """

        p = self.preferences

        # Note that we can pass an actual 'flaot' to 'set', but the preference
        # manager *always* returns preference values as strings.
        p.set("acme.ui.ratio", 1.0)
        self.assertEqual("1.0", p.get("acme.ui.ratio"))

    def test_get_and_set_bool(self):
        """ get and set bool """

        p = self.preferences

        # Note that we can pass an actual 'bool' to 'set', but the preference
        # manager *always* returns preference values as strings.
        p.set("acme.ui.visible", True)
        self.assertEqual("True", p.get("acme.ui.visible"))

    def test_get_and_set_list_of_str(self):
        """ get and set list of str """

        p = self.preferences

        # Note that we can pass an actual 'int' to 'set', but the preference
        # manager *always* returns preference values as strings.
        p.set("acme.ui.names", ["fred", "wilma", "barney"])
        self.assertEqual("['fred', 'wilma', 'barney']", p.get("acme.ui.names"))

    def test_get_and_set_list_of_int(self):
        """ get and set list of int """

        p = self.preferences

        # Note that we can pass an actual 'int' to 'set', but the preference
        # manager *always* returns preference values as strings.
        p.set("acme.ui.offsets", [1, 2, 3])
        self.assertEqual("[1, 2, 3]", p.get("acme.ui.offsets"))

    def test_empty_path(self):
        """ empty path """

        p = self.preferences

        self.assertRaises(ValueError, p.get, "")
        self.assertRaises(ValueError, p.remove, "")
        self.assertRaises(ValueError, p.set, "", "a value")

    def test_default_values(self):
        """ default values """

        p = self.preferences

        # Try non-existent names to get the default-default!
        self.assertIsNone(p.get("bogus"))
        self.assertIsNone(p.get("acme.bogus"))
        self.assertIsNone(p.get("acme.ui.bogus"))

        # Try non-existent names to get the specified default.
        self.assertEqual("a value", p.get("bogus", "a value"))
        self.assertEqual("a value", p.get("acme.bogus", "a value"))
        self.assertEqual("a value", p.get("acme.ui.bogus", "a value"))

    def test_keys(self):
        """ keys """

        p = self.preferences

        # It should be empty to start with!
        self.assertEqual([], list(p.keys()))

        # Set some preferences in the node.
        p.set("a", "1")
        p.set("b", "2")
        p.set("c", "3")

        keys = sorted(p.keys())

        self.assertEqual(["a", "b", "c"], keys)

        # Set some preferences in a child node.
        p.set("acme.a", "1")
        p.set("acme.b", "2")
        p.set("acme.c", "3")

        keys = sorted(p.keys("acme"))

        self.assertEqual(["a", "b", "c"], keys)

        # And, just to be sure, in a child of the child node ;^)
        p.set("acme.ui.a", "1")
        p.set("acme.ui.b", "2")
        p.set("acme.ui.c", "3")

        keys = sorted(p.keys("acme.ui"))

        self.assertEqual(["a", "b", "c"], keys)

        # Test keys of a non-existent node.
        self.assertEqual([], p.keys("bogus"))
        self.assertEqual([], p.keys("bogus.blargle"))
        self.assertEqual([], p.keys("bogus.blargle.foogle"))

    def test_node(self):
        """ node """

        p = self.preferences

        # Try an empty path.
        self.assertEqual(p, p.node())

        # Try a simple path.
        node = p.node("acme")
        self.assertIsNotNone(node)
        self.assertEqual("acme", node.name)
        self.assertEqual("acme", node.path)
        self.assertEqual(p, node.parent)

        # Make sure we get the same node each time we ask for it!
        self.assertEqual(node, p.node("acme"))

        # Try a nested path.
        node = p.node("acme.ui")
        self.assertIsNotNone(node)
        self.assertEqual("ui", node.name)
        self.assertEqual("acme.ui", node.path)
        self.assertEqual(p.node("acme"), node.parent)

        # And just to be sure, a really nested path.
        node = p.node("acme.ui.splash_screen")
        self.assertIsNotNone(node)
        self.assertEqual("splash_screen", node.name)
        self.assertEqual("acme.ui.splash_screen", node.path)
        self.assertEqual(p.node("acme.ui"), node.parent)

    def test_node_exists(self):
        """ node exists """

        p = self.preferences

        self.assertTrue(p.node_exists())
        self.assertFalse(p.node_exists("acme"))

        p.node("acme")
        self.assertTrue(p.node_exists("acme"))

    def test_node_names(self):
        """ node names """

        p = self.preferences

        # It should be empty to start with!
        self.assertEqual([], p.node_names())

        # Add some nodes.
        p.node("a")
        p.node("b")
        p.node("c")

        names = sorted(p.node_names())

        self.assertEqual(["a", "b", "c"], names)

        # Creatd some nodes in a child node.
        p.node("acme.a")
        p.node("acme.b")
        p.node("acme.c")

        names = sorted(p.node_names("acme"))

        self.assertEqual(["a", "b", "c"], names)

        # And, just to be sure, in a child of the child node ;^)
        p.node("acme.ui.a")
        p.node("acme.ui.b")
        p.node("acme.ui.c")

        names = sorted(p.node_names("acme.ui"))

        self.assertEqual(["a", "b", "c"], names)

        # Test keys of a non-existent node.
        self.assertEqual([], p.node_names("bogus"))
        self.assertEqual([], p.node_names("bogus.blargle"))
        self.assertEqual([], p.node_names("bogus.blargle.foogle"))

    def test_clear(self):
        """ clear """

        p = self.preferences

        # Set some values.
        p.set("acme.ui.bgcolor", "blue")
        self.assertEqual("blue", p.get("acme.ui.bgcolor"))
        p.set("acme.ui.width", 100)
        self.assertEqual("100", p.get("acme.ui.width"))

        # Clear all preferences from the node.
        p.clear("acme.ui")
        self.assertIsNone(p.get("acme.ui.bgcolor"))
        self.assertIsNone(p.get("acme.ui.width"))
        self.assertEqual(0, len(p.keys("acme.ui")))

    def test_remove(self):
        """ remove """

        p = self.preferences

        # Set a value.
        p.set("acme.ui.bgcolor", "blue")
        self.assertEqual("blue", p.get("acme.ui.bgcolor"))

        # Remove it.
        p.remove("acme.ui.bgcolor")
        self.assertIsNone(p.get("acme.ui.bgcolor"))

        # Make sure we can't remove nodes!
        p.remove("acme.ui")
        self.assertTrue(p.node_exists("acme.ui"))

    def test_flush(self):
        """ flush """

        p = self.preferences

        # A temporary .ini file for this test.
        tmp = join(self.tmpdir, "tmp.ini")

        # This could be set in the constructor of course, its just here we
        # want to use the instance declared in 'setUp'.
        p.filename = tmp

        try:
            # Load the preferences from an 'ini' file.
            p.load(self.example)

            # Flush it.
            p.flush()

            # Load it into a new node.
            p = Preferences()
            p.load(tmp)

            # Make sure it was all loaded!
            self.assertEqual("blue", p.get("acme.ui.bgcolor"))
            self.assertEqual("50", p.get("acme.ui.width"))
            self.assertEqual("1.0", p.get("acme.ui.ratio"))
            self.assertEqual("True", p.get("acme.ui.visible"))
            self.assertEqual("acme ui", p.get("acme.ui.description"))
            self.assertEqual("[1, 2, 3, 4]", p.get("acme.ui.offsets"))
            self.assertEqual("['joe', 'fred', 'jane']", p.get("acme.ui.names"))
            self.assertEqual("splash", p.get("acme.ui.splash_screen.image"))
            self.assertEqual("red", p.get("acme.ui.splash_screen.fgcolor"))

        finally:
            # Clean up!
            os.remove(tmp)

    def test_load(self):
        """ load """

        p = self.preferences

        # Load the preferences from an 'ini' file.
        p.load(self.example)

        # Make sure it was all loaded!
        self.assertEqual("blue", p.get("acme.ui.bgcolor"))
        self.assertEqual("50", p.get("acme.ui.width"))
        self.assertEqual("1.0", p.get("acme.ui.ratio"))
        self.assertEqual("True", p.get("acme.ui.visible"))
        self.assertEqual("acme ui", p.get("acme.ui.description"))
        self.assertEqual("[1, 2, 3, 4]", p.get("acme.ui.offsets"))
        self.assertEqual("['joe', 'fred', 'jane']", p.get("acme.ui.names"))
        self.assertEqual("splash", p.get("acme.ui.splash_screen.image"))
        self.assertEqual("red", p.get("acme.ui.splash_screen.fgcolor"))

    def test_load_with_filename_trait_set(self):
        """ load with filename trait set """

        p = self.preferences
        p.filename = self.example

        # Load the preferences from an 'ini' file.
        p.load()

        # Make sure it was all loaded!
        self.assertEqual("blue", p.get("acme.ui.bgcolor"))
        self.assertEqual("50", p.get("acme.ui.width"))
        self.assertEqual("1.0", p.get("acme.ui.ratio"))
        self.assertEqual("True", p.get("acme.ui.visible"))
        self.assertEqual("acme ui", p.get("acme.ui.description"))
        self.assertEqual("[1, 2, 3, 4]", p.get("acme.ui.offsets"))
        self.assertEqual("['joe', 'fred', 'jane']", p.get("acme.ui.names"))
        self.assertEqual("splash", p.get("acme.ui.splash_screen.image"))
        self.assertEqual("red", p.get("acme.ui.splash_screen.fgcolor"))

        p = self.preferences

        # Load the preferences from an 'ini' file.
        p.load(self.example)

        # Make sure it was all loaded!
        self.assertEqual("blue", p.get("acme.ui.bgcolor"))
        self.assertEqual("50", p.get("acme.ui.width"))
        self.assertEqual("1.0", p.get("acme.ui.ratio"))
        self.assertEqual("True", p.get("acme.ui.visible"))
        self.assertEqual("acme ui", p.get("acme.ui.description"))
        self.assertEqual("[1, 2, 3, 4]", p.get("acme.ui.offsets"))
        self.assertEqual("['joe', 'fred', 'jane']", p.get("acme.ui.names"))
        self.assertEqual("splash", p.get("acme.ui.splash_screen.image"))
        self.assertEqual("red", p.get("acme.ui.splash_screen.fgcolor"))

    def test_save(self):
        """ save """

        p = self.preferences

        # Load the preferences from an 'ini' file.
        p.load(self.example)

        # Make sure it was all loaded!
        self.assertEqual("blue", p.get("acme.ui.bgcolor"))
        self.assertEqual("50", p.get("acme.ui.width"))
        self.assertEqual("1.0", p.get("acme.ui.ratio"))
        self.assertEqual("True", p.get("acme.ui.visible"))
        self.assertEqual("acme ui", p.get("acme.ui.description"))
        self.assertEqual("[1, 2, 3, 4]", p.get("acme.ui.offsets"))
        self.assertEqual("['joe', 'fred', 'jane']", p.get("acme.ui.names"))
        self.assertEqual("splash", p.get("acme.ui.splash_screen.image"))
        self.assertEqual("red", p.get("acme.ui.splash_screen.fgcolor"))

        # Make a change.
        p.set("acme.ui.bgcolor", "yellow")

        # Save it to another file.
        tmp = join(self.tmpdir, "tmp.ini")
        p.save(tmp)

        try:
            # Load it into a new node.
            p = Preferences()
            p.load(tmp)

            # Make sure it was all loaded!
            self.assertEqual("yellow", p.get("acme.ui.bgcolor"))
            self.assertEqual("50", p.get("acme.ui.width"))
            self.assertEqual("1.0", p.get("acme.ui.ratio"))
            self.assertEqual("True", p.get("acme.ui.visible"))
            self.assertEqual("acme ui", p.get("acme.ui.description"))
            self.assertEqual("[1, 2, 3, 4]", p.get("acme.ui.offsets"))
            self.assertEqual("['joe', 'fred', 'jane']", p.get("acme.ui.names"))
            self.assertEqual("splash", p.get("acme.ui.splash_screen.image"))
            self.assertEqual("red", p.get("acme.ui.splash_screen.fgcolor"))

        finally:
            # Clean up!
            os.remove(tmp)

    def SKIPtest_dump(self):
        """ dump """

        # This make look like a weird test, since we don't ever actually check
        # anything, but it is useful for people to see the structure of a
        # preferences hierarchy.
        p = self.preferences

        # Load the preferences from an 'ini' file.
        p.load(self.example)
        p.dump()

    def test_get_inherited(self):
        """ get inherited """

        p = self.preferences

        # Set a string preference.
        p.set("bgcolor", "red")
        p.set("acme.bgcolor", "green")
        p.set("acme.ui.bgcolor", "blue")

        self.assertEqual("blue", p.get("acme.ui.bgcolor", inherit=True))

        # Now remove the 'lowest' layer.
        p.remove("acme.ui.bgcolor")
        self.assertEqual("green", p.get("acme.ui.bgcolor", inherit=True))

        # And the next one.
        p.remove("acme.bgcolor")
        self.assertEqual("red", p.get("acme.ui.bgcolor", inherit=True))

        # And the last one.
        p.remove("bgcolor")
        self.assertEqual(None, p.get("acme.ui.bgcolor", inherit=True))

    def test_add_listener(self):
        """ add listener """

        p = self.preferences

        def listener(node, key, old, new):
            """ Listener for changes to a preferences node. """

            listener.node = node
            listener.key = key
            listener.old = old
            listener.new = new

        # Add a listener.
        p.add_preferences_listener(listener, "acme.ui")

        # Set a value and make sure the listener was called.
        p.set("acme.ui.bgcolor", "blue")
        self.assertEqual(p.node("acme.ui"), listener.node)
        self.assertEqual("bgcolor", listener.key)
        self.assertIsNone(listener.old)
        self.assertEqual("blue", listener.new)

        # Set it to another value to make sure we get the 'old' value
        # correctly.
        p.set("acme.ui.bgcolor", "red")
        self.assertEqual(p.node("acme.ui"), listener.node)
        self.assertEqual("bgcolor", listener.key)
        self.assertEqual("blue", listener.old)
        self.assertEqual("red", listener.new)

    def test_remove_listener(self):
        """ remove listener """

        p = self.preferences

        def listener(node, key, old, new):
            """ Listener for changes to a preferences node. """

            listener.node = node
            listener.key = key
            listener.old = old
            listener.new = new

        # Add a listener.
        p.add_preferences_listener(listener, "acme.ui")

        # Set a value and make sure the listener was called.
        p.set("acme.ui.bgcolor", "blue")
        self.assertEqual(p.node("acme.ui"), listener.node)
        self.assertEqual("bgcolor", listener.key)
        self.assertIsNone(listener.old)
        self.assertEqual("blue", listener.new)

        # Remove the listener.
        p.remove_preferences_listener(listener, "acme.ui")

        # Set a value and make sure the listener was *not* called.
        listener.node = None

        p.set("acme.ui.bgcolor", "blue")
        self.assertIsNone(listener.node)

    def test_set_with_same_value(self):
        """ set with same value """

        p = self.preferences

        def listener(node, key, old, new):
            """ Listener for changes to a preferences node. """

            listener.node = node
            listener.key = key
            listener.old = old
            listener.new = new

        # Add a listener.
        p.add_preferences_listener(listener, "acme.ui")

        # Set a value and make sure the listener was called.
        p.set("acme.ui.bgcolor", "blue")
        self.assertEqual(p.node("acme.ui"), listener.node)
        self.assertEqual("bgcolor", listener.key)
        self.assertIsNone(listener.old)
        self.assertEqual("blue", listener.new)

        # Clear out the listener.
        listener.node = None

        # Set the same value and make sure the listener *doesn't* get called.
        p.set("acme.ui.bgcolor", "blue")
        self.assertIsNone(listener.node)
