# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Tests for scoped preferences. """


# Standard library imports.
import os
import tempfile
from os.path import join

# Major package imports.
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

# Enthought library imports.
from apptools.preferences.api import Preferences, ScopedPreferences

# Local imports.
from .test_preferences import PreferencesTestCase


# This module's package.
PKG = "apptools.preferences.tests"


class ScopedPreferencesTestCase(PreferencesTestCase):
    """ Tests for the scoped preferences. """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        # A temporary directory that can safely be written to.
        self.tmpdir = tempfile.mkdtemp()

        self.preferences = ScopedPreferences(
            application_preferences_filename=os.path.join(
                self.tmpdir, "preferences.ini"
            )
        )

        # The filename of the example preferences file.
        self.example = os.fspath(files(PKG) / "example.ini")

    def tearDown(self):
        """ Called immediately after each test method has been called. """

        # Remove the temporary directory.
        os.rmdir(self.tmpdir)

    ###########################################################################
    # Tests overridden from 'PreferencesTestCase'.
    ###########################################################################

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
        self.assertEqual(p.node("application/"), node.parent)

        # Make sure we get the same node each time we ask for it!
        self.assertEqual(node, p.node("acme"))

        # Try a nested path.
        node = p.node("acme.ui")
        self.assertIsNotNone(node)
        self.assertEqual("ui", node.name)
        self.assertEqual("acme.ui", node.path)
        self.assertEqual(p.node("application/acme"), node.parent)

        # And just to be sure, a really nested path.
        node = p.node("acme.ui.splash_screen")
        self.assertIsNotNone(node)
        self.assertEqual("splash_screen", node.name)
        self.assertEqual("acme.ui.splash_screen", node.path)
        self.assertEqual(p.node("application/acme.ui"), node.parent)

    def test_save(self):
        """ save """

        p = self.preferences

        # Get the application scope.
        application = p.node("application/")

        tmp = join(self.tmpdir, "test.ini")
        application.filename = tmp

        # Set a value.
        p.set("acme.ui.bgcolor", "red")

        # Save all scopes.
        p.save()

        # Make sure a file was written.
        self.assertTrue(os.path.exists(tmp))

        # Load the 'ini' file into a new preferences node and make sure the
        # preference is in there.
        p = Preferences()
        p.load(tmp)

        self.assertEqual("red", p.get("acme.ui.bgcolor"))

        # Cleanup.
        os.remove(tmp)

    ###########################################################################
    # Tests.
    ###########################################################################

    def test_ability_to_specify_primary_scope(self):

        preferences = ScopedPreferences(
            scopes=[
                Preferences(name="a"),
                Preferences(name="b"),
                Preferences(name="c"),
            ],
            primary_scope_name="b",
        )

        # This should set the prefrrence in the primary scope.
        preferences.set("acme.foo", "bar")

        # Look it up specifically in the primary scope.
        self.assertEqual("bar", preferences.get("b/acme.foo"))

    def test_builtin_scopes(self):
        """ builtin scopes """

        p = self.preferences

        # Make sure the default built-in scopes get created.
        self.assertTrue(p.node_exists("application/"))
        self.assertTrue(p.node_exists("default/"))

    def test_get_and_set_in_specific_scope(self):
        """ get and set in specific scope """

        p = self.preferences

        # Set a preference and make sure we can get it again!
        p.set("default/acme.ui.bgcolor", "red")
        self.assertEqual("red", p.get("default/acme.ui.bgcolor"))

    def test_clear_in_specific_scope(self):
        """ clear in specific scope """

        p = self.preferences

        # Set a value in both the application and default scopes.
        p.set("application/acme.ui.bgcolor", "red")
        p.set("default/acme.ui.bgcolor", "yellow")

        # Make sure when we look it up we get the one in first scope in the
        # lookup order.
        self.assertEqual("red", p.get("acme.ui.bgcolor"))

        # Now clear out the application scope.
        p.clear("application/acme.ui")
        self.assertEqual(0, len(p.keys("application/acme.ui")))

        # We should now get the value from the default scope.
        self.assertEqual("yellow", p.get("acme.ui.bgcolor"))

    def test_remove_in_specific_scope(self):
        """ remove in specific scope """

        p = self.preferences

        # Set a value in both the application and default scopes.
        p.set("application/acme.ui.bgcolor", "red")
        p.set("default/acme.ui.bgcolor", "yellow")

        # Make sure when we look it up we get the one in first scope in the
        # lookup order.
        self.assertEqual("red", p.get("acme.ui.bgcolor"))

        # Now remove it from the application scope.
        p.remove("application/acme.ui.bgcolor")

        # We should now get the value from the default scope.
        self.assertEqual("yellow", p.get("acme.ui.bgcolor"))

    def test_keys_in_specific_scope(self):
        """ keys in specific scope """

        p = self.preferences

        # It should be empty to start with!
        self.assertEqual([], p.keys("default/"))

        # Set some preferences in the node.
        p.set("default/a", "1")
        p.set("default/b", "2")
        p.set("default/c", "3")

        keys = p.keys("default/")
        keys.sort()

        self.assertEqual(["a", "b", "c"], keys)

        # Set some preferences in a child node.
        p.set("default/acme.a", "1")
        p.set("default/acme.b", "2")
        p.set("default/acme.c", "3")

        keys = p.keys("default/acme")
        keys.sort()

        self.assertEqual(["a", "b", "c"], keys)

        # And, just to be sure, in a child of the child node ;^)
        p.set("default/acme.ui.a", "1")
        p.set("default/acme.ui.b", "2")
        p.set("default/acme.ui.c", "3")

        keys = p.keys("default/acme.ui")
        keys.sort()

        self.assertEqual(["a", "b", "c"], keys)

    def test_node_in_specific_scope(self):
        """ node in specific scope """

        p = self.preferences

        # Try an empty path.
        self.assertEqual(p, p.node())

        # Try a simple path.
        node = p.node("default/acme")
        self.assertIsNotNone(node)
        self.assertEqual("acme", node.name)
        self.assertEqual("acme", node.path)
        self.assertEqual(p.node("default/"), node.parent)

        # Make sure we get the same node each time we ask for it!
        self.assertEqual(node, p.node("default/acme"))

        # Try a nested path.
        node = p.node("default/acme.ui")
        self.assertIsNotNone(node)
        self.assertEqual("ui", node.name)
        self.assertEqual("acme.ui", node.path)
        self.assertEqual(p.node("default/acme"), node.parent)

        # And just to be sure, a really nested path.
        node = p.node("default/acme.ui.splash_screen")
        self.assertIsNotNone(node)
        self.assertEqual("splash_screen", node.name)
        self.assertEqual("acme.ui.splash_screen", node.path)
        self.assertEqual(p.node("default/acme.ui"), node.parent)

    def test_node_exists_in_specific_scope(self):
        """ node exists """

        p = self.preferences

        self.assertTrue(p.node_exists())
        self.assertFalse(p.node_exists("default/acme"))

        p.node("default/acme")
        self.assertTrue(p.node_exists("default/acme"))

    def test_node_names_in_specific_scope(self):
        """ node names in specific scope """

        p = self.preferences

        # It should be empty to start with!
        self.assertEqual([], p.node_names("default/"))

        # Create some nodes.
        p.node("default/a")
        p.node("default/b")
        p.node("default/c")

        names = p.node_names("default/")
        names.sort()

        self.assertEqual(["a", "b", "c"], names)

        # Creatd some nodes in a child node.
        p.node("default/acme.a")
        p.node("default/acme.b")
        p.node("default/acme.c")

        names = p.node_names("default/acme")
        names.sort()

        self.assertEqual(["a", "b", "c"], names)

        # And, just to be sure, in a child of the child node ;^)
        p.node("default/acme.ui.a")
        p.node("default/acme.ui.b")
        p.node("default/acme.ui.c")

        names = p.node_names("default/acme.ui")
        names.sort()

        self.assertEqual(["a", "b", "c"], names)

    def test_default_lookup_order(self):
        """ default lookup order """

        p = self.preferences

        # Set a value in both the application and default scopes.
        p.set("application/acme.ui.bgcolor", "red")
        p.set("default/acme.ui.bgcolor", "yellow")

        # Make sure when we look it up we get the one in first scope in the
        # lookup order.
        self.assertEqual("red", p.get("acme.ui.bgcolor"))

        # But we can still get at each scope individually.
        self.assertEqual("red", p.get("application/acme.ui.bgcolor"))
        self.assertEqual("yellow", p.get("default/acme.ui.bgcolor"))

    def test_lookup_order(self):
        """ lookup order """

        p = self.preferences
        p.lookup_order = ["default", "application"]

        # Set a value in both the application and default scopes.
        p.set("application/acme.ui.bgcolor", "red")
        p.set("default/acme.ui.bgcolor", "yellow")

        # Make sure when we look it up we get the one in first scope in the
        # lookup order.
        self.assertEqual("red", p.get("acme.ui.bgcolor"))

        # But we can still get at each scope individually.
        self.assertEqual("red", p.get("application/acme.ui.bgcolor"))
        self.assertEqual("yellow", p.get("default/acme.ui.bgcolor"))

    def test_add_listener_in_specific_scope(self):
        """ add listener in specific scope. """

        p = self.preferences

        def listener(node, key, old, new):
            """ Listener for changes to a preferences node. """

            listener.node = node
            listener.key = key
            listener.old = old
            listener.new = new

        # Add a listener.
        p.add_preferences_listener(listener, "default/acme.ui")

        # Set a value and make sure the listener was called.
        p.set("default/acme.ui.bgcolor", "blue")
        self.assertEqual(p.node("default/acme.ui"), listener.node)
        self.assertEqual("bgcolor", listener.key)
        self.assertIsNone(listener.old)
        self.assertEqual("blue", listener.new)

        # Set it to another value to make sure we get the 'old' value
        # correctly.
        p.set("default/acme.ui.bgcolor", "red")
        self.assertEqual(p.node("default/acme.ui"), listener.node)
        self.assertEqual("bgcolor", listener.key)
        self.assertEqual("blue", listener.old)
        self.assertEqual("red", listener.new)

    def test_remove_listener_in_specific_scope(self):
        """ remove listener in specific scope. """

        p = self.preferences

        def listener(node, key, old, new):
            """ Listener for changes to a preferences node. """

            listener.node = node
            listener.key = key
            listener.old = old
            listener.new = new

        # Add a listener.
        p.add_preferences_listener(listener, "default/acme.ui")

        # Set a value and make sure the listener was called.
        p.set("default/acme.ui.bgcolor", "blue")
        self.assertEqual(p.node("default/acme.ui"), listener.node)
        self.assertEqual("bgcolor", listener.key)
        self.assertIsNone(listener.old)
        self.assertEqual("blue", listener.new)

        # Remove the listener.
        p.remove_preferences_listener(listener, "default/acme.ui")

        # Set a value and make sure the listener was *not* called.
        listener.node = None

        p.set("default/acme.ui.bgcolor", "blue")
        self.assertIsNone(listener.node)

    def test_non_existent_scope(self):
        """ non existent scope """

        p = self.preferences

        self.assertRaises(ValueError, p.get, "bogus/acme.ui.bgcolor")
