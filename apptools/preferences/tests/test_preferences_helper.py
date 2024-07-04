# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Tests for the preferences helper. """


# Standard library imports.
import os
import shutil
import tempfile
import unittest

# Major package imports.
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

# Enthought library imports.
from apptools.preferences.api import Preferences, PreferencesHelper
from apptools.preferences.api import ScopedPreferences
from apptools.preferences.api import set_default_preferences
from apptools._testing.optional_dependencies import requires_configobj

from traits.api import (
    Any, Bool, HasTraits, Int, Float, List, Str, TraitError,
    push_exception_handler, pop_exception_handler,
)
from traits.observation.api import match


def width_listener(event):

    width_listener.obj = event.object
    width_listener.trait_name = event.name
    width_listener.old = event.old
    width_listener.new = event.new


def bgcolor_listener(event):

    bgcolor_listener.obj = event.object
    bgcolor_listener.trait_name = event.name
    bgcolor_listener.old = event.old
    bgcolor_listener.new = event.new


# This module's package.
PKG = "apptools.preferences.tests"


@requires_configobj
class PreferencesHelperTestCase(unittest.TestCase):
    """ Tests for the preferences helper. """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        self.preferences = set_default_preferences(Preferences())

        # The filename of the example preferences file.
        self.example = os.fspath(files(PKG) / "example.ini")

        # A temporary directory that can safely be written to.
        self.tmpdir = tempfile.mkdtemp()

        # Path to a temporary file
        self.tmpfile = os.path.join(self.tmpdir, "tmp.ini")

        push_exception_handler(reraise_exceptions=True)
        self.addCleanup(pop_exception_handler)

    def tearDown(self):
        """ Called immediately after each test method has been called. """

        # Remove the temporary directory.
        shutil.rmtree(self.tmpdir)

    ###########################################################################
    # Tests.
    ###########################################################################

    def test_class_scope_preferences_path(self):
        """ class scope preferences path """

        p = self.preferences
        p.load(self.example)

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The path to the preferences node that contains our preferences.
            preferences_path = "acme.ui"

            # The traits that we want to initialize from preferences.
            bgcolor = Str
            width = Int
            ratio = Float
            visible = Bool
            description = Str
            offsets = List(Int)
            names = List(Str)

        helper = AcmeUIPreferencesHelper()
        helper.observe(bgcolor_listener, match(lambda n, t: True))

        # Make sure the helper was initialized properly.
        self.assertEqual("blue", helper.bgcolor)
        self.assertEqual(50, helper.width)
        self.assertEqual(1.0, helper.ratio)
        self.assertTrue(helper.visible)
        self.assertEqual("acme ui", helper.description)
        self.assertEqual([1, 2, 3, 4], helper.offsets)
        self.assertEqual(["joe", "fred", "jane"], helper.names)

        # Make sure we can set the preference via the helper...
        helper.bgcolor = "yellow"
        self.assertEqual("yellow", p.get("acme.ui.bgcolor"))
        self.assertEqual("yellow", helper.bgcolor)

        # ... and that the correct trait change event was fired.
        self.assertEqual(helper, bgcolor_listener.obj)
        self.assertEqual("bgcolor", bgcolor_listener.trait_name)
        self.assertEqual("blue", bgcolor_listener.old)
        self.assertEqual("yellow", bgcolor_listener.new)

        # Make sure we can set the preference via the preferences node...
        p.set("acme.ui.bgcolor", "red")
        self.assertEqual("red", p.get("acme.ui.bgcolor"))
        self.assertEqual("red", helper.bgcolor)

        # ... and that the correct trait change event was fired.
        self.assertEqual(helper, bgcolor_listener.obj)
        self.assertEqual("bgcolor", bgcolor_listener.trait_name)
        self.assertEqual("yellow", bgcolor_listener.old)
        self.assertEqual("red", bgcolor_listener.new)

    def test_instance_scope_preferences_path(self):
        """ instance scope preferences path """

        p = self.preferences
        p.load(self.example)

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The traits that we want to initialize from preferences.
            bgcolor = Str
            width = Int
            ratio = Float
            visible = Bool
            description = Str
            offsets = List(Int)
            names = List(Str)

        helper = AcmeUIPreferencesHelper(preferences_path="acme.ui")
        helper.observe(bgcolor_listener, match(lambda n, t: True))

        # Make sure the helper was initialized properly.
        self.assertEqual("blue", helper.bgcolor)
        self.assertEqual(50, helper.width)
        self.assertEqual(1.0, helper.ratio)
        self.assertTrue(helper.visible)
        self.assertEqual("acme ui", helper.description)
        self.assertEqual([1, 2, 3, 4], helper.offsets)
        self.assertEqual(["joe", "fred", "jane"], helper.names)

        # Make sure we can set the preference via the helper...
        helper.bgcolor = "yellow"
        self.assertEqual("yellow", p.get("acme.ui.bgcolor"))
        self.assertEqual("yellow", helper.bgcolor)

        # ... and that the correct trait change event was fired.
        self.assertEqual(helper, bgcolor_listener.obj)
        self.assertEqual("bgcolor", bgcolor_listener.trait_name)
        self.assertEqual("blue", bgcolor_listener.old)
        self.assertEqual("yellow", bgcolor_listener.new)

        # Make sure we can set the preference via the preferences node...
        p.set("acme.ui.bgcolor", "red")
        self.assertEqual("red", p.get("acme.ui.bgcolor"))
        self.assertEqual("red", helper.bgcolor)

        # ... and that the correct trait change event was fired.
        self.assertEqual(helper, bgcolor_listener.obj)
        self.assertEqual("bgcolor", bgcolor_listener.trait_name)
        self.assertEqual("yellow", bgcolor_listener.old)
        self.assertEqual("red", bgcolor_listener.new)

    def test_default_values(self):
        """ default values """

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The path to the preferences node that contains our preferences.
            preferences_path = "acme.ui"

            # The traits that we want to initialize from preferences.
            bgcolor = Str("blue")
            width = Int(50)
            ratio = Float(1.0)
            visible = Bool(True)
            description = Str("description")
            offsets = List(Int, [1, 2, 3, 4])
            names = List(Str, ["joe", "fred", "jane"])

        helper = AcmeUIPreferencesHelper()

        # Make sure the helper was initialized properly.
        self.assertEqual("blue", helper.bgcolor)
        self.assertEqual(50, helper.width)
        self.assertEqual(1.0, helper.ratio)
        self.assertTrue(helper.visible)
        self.assertEqual("description", helper.description)
        self.assertEqual([1, 2, 3, 4], helper.offsets)
        self.assertEqual(["joe", "fred", "jane"], helper.names)

    def test_real_unicode_values(self):
        """ Test with real life unicode values """

        p = self.preferences
        p.load(self.example)

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The path to the preferences node that contains our preferences.
            preferences_path = "acme.ui"

            # The traits that we want to initialize from preferences.
            bgcolor = Str("blue")
            width = Int(50)
            ratio = Float(1.0)
            visible = Bool(True)
            description = Str("")
            offsets = List(Int, [1, 2, 3, 4])
            names = List(Str, ["joe", "fred", "jane"])

        helper = AcmeUIPreferencesHelper()

        first_unicode_str = "U\xdc\xf2ser"

        helper.description = first_unicode_str
        self.assertEqual(first_unicode_str, helper.description)

        second_unicode_str = "caf\xe9"
        helper.description = second_unicode_str
        self.assertEqual(second_unicode_str, helper.description)
        self.assertEqual(second_unicode_str, p.get("acme.ui.description"))

        # Save it to another file.
        tmp = os.path.join(self.tmpdir, "tmp.ini")
        p.save(tmp)

        # Load it into a new node.
        p = Preferences()
        p.load(tmp)
        self.assertEqual(second_unicode_str, p.get("acme.ui.description"))
        self.assertEqual("True", p.get("acme.ui.visible"))
        self.assertTrue(helper.visible)

    def test_mutate_list_of_values(self):
        """ Mutated list should be saved and _items events not to be
        saved in the preferences.
        """
        # Regression test for enthought/apptools#129

        class MyPreferencesHelper(PreferencesHelper):
            preferences_path = Str('my_section')

            list_of_str = List(Str)

        helper = MyPreferencesHelper(list_of_str=["1"])

        # Now modify the list to fire _items event
        helper.list_of_str.append("2")
        self.preferences.save(self.tmpfile)

        new_preferences = Preferences()
        new_preferences.load(self.tmpfile)

        self.assertEqual(
            new_preferences.get("my_section.list_of_str"), str(["1", "2"])
        )
        self.assertEqual(new_preferences.keys("my_section"), ["list_of_str"])

    def test_sync_anytrait_items_not_event(self):
        """ Test sychronizing trait with name *_items which is a normal trait
        rather than an event trait for listening to list/dict/set mutation.
        """

        class MyPreferencesHelper(PreferencesHelper):
            preferences_path = Str('my_section')

            names_items = Str()

        helper = MyPreferencesHelper(preferences=self.preferences)
        helper.names_items = "Hello"

        self.preferences.save(self.tmpfile)
        new_preferences = Preferences()
        new_preferences.load(self.tmpfile)

        self.assertEqual(
            sorted(new_preferences.keys("my_section")),
            ["names_items"]
        )
        self.assertEqual(
            new_preferences.get("my_section.names_items"),
            str(helper.names_items),
        )

    def test_no_preferences_path(self):
        """ no preferences path """

        p = self.preferences
        p.load(self.example)

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The traits that we want to initialize from preferences.
            bgcolor = Str
            width = Int
            ratio = Float
            visible = Bool
            description = Str
            offsets = List(Int)
            names = List(Str)

        # Cannot create a helper with a preferences path.
        self.assertRaises(SystemError, AcmeUIPreferencesHelper)

    def test_sync_trait(self):
        """ sync trait """

        class Widget(HasTraits):
            """ A widget! """

            background_color = Str

        w = Widget()
        w.observe(bgcolor_listener, match(lambda n, t: True))

        p = self.preferences
        p.load(self.example)

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The path to the preferences node that contains our preferences.
            preferences_path = "acme.ui"

            # The traits that we want to initialize from preferences.
            bgcolor = Str
            width = Int
            ratio = Float
            visible = Bool
            description = Str
            offsets = List(Int)
            names = List(Str)

        helper = AcmeUIPreferencesHelper()
        helper.sync_trait("bgcolor", w, "background_color")

        # Make sure the helper was initialized properly.
        self.assertEqual("blue", helper.bgcolor)
        self.assertEqual(50, helper.width)
        self.assertEqual(1.0, helper.ratio)
        self.assertTrue(helper.visible)
        self.assertEqual("acme ui", helper.description)
        self.assertEqual([1, 2, 3, 4], helper.offsets)
        self.assertEqual(["joe", "fred", "jane"], helper.names)

        self.assertEqual("blue", w.background_color)

        # Make sure we can set the preference via the helper...
        helper.bgcolor = "yellow"
        self.assertEqual("yellow", p.get("acme.ui.bgcolor"))
        self.assertEqual("yellow", helper.bgcolor)

        self.assertEqual("yellow", w.background_color)

        # ... and that the correct trait change event was fired.
        self.assertEqual(w, bgcolor_listener.obj)
        self.assertEqual("background_color", bgcolor_listener.trait_name)
        self.assertEqual("blue", bgcolor_listener.old)
        self.assertEqual("yellow", bgcolor_listener.new)

        # Make sure we can set the preference via the preferences node...
        p.set("acme.ui.bgcolor", "red")
        self.assertEqual("red", p.get("acme.ui.bgcolor"))
        self.assertEqual("red", helper.bgcolor)

        self.assertEqual("red", w.background_color)

        # ... and that the correct trait change event was fired.
        self.assertEqual(w, bgcolor_listener.obj)
        self.assertEqual("background_color", bgcolor_listener.trait_name)
        self.assertEqual("yellow", bgcolor_listener.old)
        self.assertEqual("red", bgcolor_listener.new)

    def test_scoped_preferences(self):
        """ scoped preferences """

        p = set_default_preferences(
            ScopedPreferences(application_preferences_filename=self.tmpfile)
        )

        # Set a preference value in the default scope.
        p.set("default/acme.ui.bgcolor", "blue")

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The path to the preferences node that contains our preferences.
            preferences_path = "acme.ui"

            # The traits that we want to initialize from preferences.
            bgcolor = Str

            # A trait for a preference that does not exist yet.
            name = Str

        helper = AcmeUIPreferencesHelper()

        # Make sure the trait is set!
        self.assertEqual("blue", helper.bgcolor)

        # And that the non-existent trait gets the default value.
        self.assertEqual("", helper.name)

    def test_preference_not_in_file(self):
        """ preference not in file """

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The path to the preferences node that contains our preferences.
            preferences_path = "acme.ui"

            # A trait that has no corresponding value in the file.
            title = Str("Acme")

        helper = AcmeUIPreferencesHelper()

        # Make sure the trait is set!
        self.assertEqual("Acme", helper.title)

        # Set a new value.
        helper.title = "Acme Plus"

        # Make sure the trait is set!
        self.assertEqual("Acme Plus", helper.title)
        self.assertEqual("Acme Plus", self.preferences.get("acme.ui.title"))

    def test_preferences_node_changed(self):
        """ preferences node changed """

        p = self.preferences
        p.load(self.example)

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The path to the preferences node that contains our preferences.
            preferences_path = "acme.ui"

            # The traits that we want to initialize from preferences.
            bgcolor = Str
            width = Int
            ratio = Float
            visible = Bool
            description = Str
            offsets = List(Int)
            names = List(Str)

        helper = AcmeUIPreferencesHelper()

        # We only listen to some of the traits so the testing is easier.
        helper.observe(width_listener, ["width"])
        helper.observe(bgcolor_listener, ["bgcolor"])

        # Create a new preference node.
        p1 = Preferences()
        p1.load(self.example)

        p1.set("acme.ui.bgcolor", "red")
        p1.set("acme.ui.width", 40)

        # Set the new preferences
        helper.preferences = p1

        # Test event handling.
        self.assertEqual(helper, width_listener.obj)
        self.assertEqual("width", width_listener.trait_name)
        self.assertEqual(50, width_listener.old)
        self.assertEqual(40, width_listener.new)

        self.assertEqual(helper, bgcolor_listener.obj)
        self.assertEqual("bgcolor", bgcolor_listener.trait_name)
        self.assertEqual("blue", bgcolor_listener.old)
        self.assertEqual("red", bgcolor_listener.new)

        # Test re-initialization.
        self.assertEqual(helper.bgcolor, "red")
        self.assertEqual(helper.width, 40)

        # Test event handling.
        p1.set("acme.ui.bgcolor", "black")
        self.assertEqual(helper, bgcolor_listener.obj)
        self.assertEqual("bgcolor", bgcolor_listener.trait_name)
        self.assertEqual("red", bgcolor_listener.old)
        self.assertEqual("black", bgcolor_listener.new)

        # This should not trigger any new changes since we are setting values
        # on the old preferences node.
        p.set("acme.ui.bgcolor", "white")
        self.assertEqual(helper, bgcolor_listener.obj)
        self.assertEqual("bgcolor", bgcolor_listener.trait_name)
        self.assertEqual("red", bgcolor_listener.old)
        self.assertEqual("black", bgcolor_listener.new)

    def test_nested_set_in_trait_change_handler(self):
        """ nested set in trait change handler """

        p = self.preferences
        p.load(self.example)

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The traits that we want to initialize from preferences.
            bgcolor = Str
            width = Int
            ratio = Float
            visible = Bool
            description = Str
            offsets = List(Int)
            names = List(Str)

            # When the width changes, change the ratio.
            def _width_changed(self, trait_name, old, new):
                """ Static trait change handler. """

                self.ratio = 3.0

        helper = AcmeUIPreferencesHelper(preferences_path="acme.ui")

        # Make sure the helper was initialized properly.
        self.assertEqual("blue", helper.bgcolor)
        self.assertEqual(50, helper.width)
        self.assertEqual(1.0, helper.ratio)
        self.assertTrue(helper.visible)
        self.assertEqual("acme ui", helper.description)
        self.assertEqual([1, 2, 3, 4], helper.offsets)
        self.assertEqual(["joe", "fred", "jane"], helper.names)

        # Change the width via the preferences node. This should cause the
        # ratio to get set via the static trait change handler on the helper.
        p.set("acme.ui.width", 42)
        self.assertEqual(42, helper.width)
        self.assertEqual("42", p.get("acme.ui.width"))

        # Did the ratio get changed?
        self.assertEqual(3.0, helper.ratio)
        self.assertEqual("3.0", p.get("acme.ui.ratio"))

    # fixme: No comments - nice work... I added the doc string and the 'return'
    # to be compatible with the rest of the module. Interns please note correct
    # procedure when modifying existing code. If in doubt, ask a developer.
    def test_unevaluated_strings(self):
        """ unevaluated strings """

        p = self.preferences
        p.load(self.example)

        class AcmeUIPreferencesHelper(PreferencesHelper):
            width = Any(is_str=True)

        helper = AcmeUIPreferencesHelper(preferences_path="acme.ui")

        self.assertEqual("50", helper.width)

    def test_invalid_preference(self):

        p = self.preferences
        p.load(self.example)

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ The Acme UI class! """

            # The traits that we want to initialize from preferences.
            invalid = Int

        # attempt to create instance from invalid value
        with self.assertRaises(TraitError):
            AcmeUIPreferencesHelper(preferences_path="acme.ui")

    def test_preferences_not_written_on_helper_creation(self):

        class AppPreferencesHelper(PreferencesHelper):
            #: The node that contains the preferences.
            preferences_path = "app"

            #: The user's favourite colour
            color = Str()

        default_preferences = Preferences(name="default")
        default_preferences.set("app.color", "red")

        application_preferences = Preferences(name="application")
        preferences = ScopedPreferences(
            scopes=[application_preferences, default_preferences]
        )
        self.assertIsNone(application_preferences.get("app.color"))

        # Then creation of the helper should not cause the application
        # preferences to change.
        AppPreferencesHelper(preferences=preferences)
        self.assertIsNone(application_preferences.get("app.color"))
