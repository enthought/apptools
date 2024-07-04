# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Tests for preference bindings. """


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
from apptools.preferences.api import Preferences
from apptools.preferences.api import bind_preference
from apptools.preferences.api import set_default_preferences
from apptools._testing.optional_dependencies import requires_configobj

from traits.api import Bool, HasTraits, Int, Float, Str, TraitError
from traits.observation.api import match


# This module's package.
PKG = "apptools.preferences.tests"


def listener(event):
    """ A useful trait change handler for testing! """

    listener.obj = event.object
    listener.trait_name = event.name
    listener.old = event.old
    listener.new = event.new


@requires_configobj
class PreferenceBindingTestCase(unittest.TestCase):
    """ Tests for preference bindings. """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        self.preferences = set_default_preferences(Preferences())

        # The filename of the example preferences file.
        self.example = os.fspath(files(PKG) / "example.ini")

    def tearDown(self):
        """ Called immediately after each test method has been called. """

    ###########################################################################
    # Tests.
    ###########################################################################

    def test_preference_binding(self):
        """ preference binding """

        p = self.preferences
        p.load(self.example)

        class AcmeUI(HasTraits):
            """ The Acme UI class! """

            # The traits that we want to initialize from preferences.
            bgcolor = Str
            width = Int
            ratio = Float
            visible = Bool

        acme_ui = AcmeUI()
        acme_ui.observe(listener, match(lambda n, t: True))

        # Make some bindings.
        bind_preference(acme_ui, "bgcolor", "acme.ui.bgcolor")
        bind_preference(acme_ui, "width", "acme.ui.width")
        bind_preference(acme_ui, "ratio", "acme.ui.ratio")
        bind_preference(acme_ui, "visible", "acme.ui.visible")

        # Make sure the object was initialized properly.
        self.assertEqual("blue", acme_ui.bgcolor)
        self.assertEqual(50, acme_ui.width)
        self.assertEqual(1.0, acme_ui.ratio)
        self.assertTrue(acme_ui.visible)

        # Make sure we can set the preference via the helper...
        acme_ui.bgcolor = "yellow"
        self.assertEqual("yellow", p.get("acme.ui.bgcolor"))
        self.assertEqual("yellow", acme_ui.bgcolor)

        # ... and that the correct trait change event was fired.
        self.assertEqual(acme_ui, listener.obj)
        self.assertEqual("bgcolor", listener.trait_name)
        self.assertEqual("blue", listener.old)
        self.assertEqual("yellow", listener.new)

        # Make sure we can set the preference via the preferences node...
        p.set("acme.ui.bgcolor", "red")
        self.assertEqual("red", p.get("acme.ui.bgcolor"))
        self.assertEqual("red", acme_ui.bgcolor)

        # ... and that the correct trait change event was fired.
        self.assertEqual(acme_ui, listener.obj)
        self.assertEqual("bgcolor", listener.trait_name)
        self.assertEqual("yellow", listener.old)
        self.assertEqual("red", listener.new)

        # Make sure we can set a non-string preference via the helper...
        acme_ui.ratio = 0.5
        self.assertEqual("0.5", p.get("acme.ui.ratio"))
        self.assertEqual(0.5, acme_ui.ratio)

        # Make sure we can set a non-string preference via the node...
        p.set("acme.ui.ratio", "0.75")
        self.assertEqual("0.75", p.get("acme.ui.ratio"))
        self.assertEqual(0.75, acme_ui.ratio)

    def test_default_values(self):
        """ instance scope preferences path """

        class AcmeUI(HasTraits):
            """ The Acme UI class! """

            # The traits that we want to initialize from preferences.
            bgcolor = Str("blue")
            width = Int(50)
            ratio = Float(1.0)
            visible = Bool(True)

        acme_ui = AcmeUI()

        # Make some bindings.
        bind_preference(acme_ui, "bgcolor", "acme.ui.bgcolor")
        bind_preference(acme_ui, "width", "acme.ui.width")
        bind_preference(acme_ui, "ratio", "acme.ui.ratio")
        bind_preference(acme_ui, "visible", "acme.ui.visible")

        # Make sure the helper was initialized properly.
        self.assertEqual("blue", acme_ui.bgcolor)
        self.assertEqual(50, acme_ui.width)
        self.assertEqual(1.0, acme_ui.ratio)
        self.assertTrue(acme_ui.visible)

    def test_load_and_save(self):
        """ load and save """

        p = self.preferences
        p.load(self.example)

        class AcmeUI(HasTraits):
            """ The Acme UI class! """

            # The traits that we want to initialize from preferences.
            bgcolor = Str("red")
            width = Int(60)
            ratio = Float(2.0)
            visible = Bool(False)

        acme_ui = AcmeUI()

        # Make some bindings.
        bind_preference(acme_ui, "bgcolor", "acme.ui.bgcolor")
        bind_preference(acme_ui, "width", "acme.ui.width")
        bind_preference(acme_ui, "ratio", "acme.ui.ratio")
        bind_preference(acme_ui, "visible", "acme.ui.visible")

        # Make sure the helper was initialized properly (with the values in
        # the loaded .ini file *not* the trait defaults!).
        self.assertEqual("blue", acme_ui.bgcolor)
        self.assertEqual(50, acme_ui.width)
        self.assertEqual(1.0, acme_ui.ratio)
        self.assertTrue(acme_ui.visible)

        # Make a change to one of the preference values.
        p.set("acme.ui.bgcolor", "yellow")
        self.assertEqual("yellow", acme_ui.bgcolor)
        self.assertEqual("yellow", p.get("acme.ui.bgcolor"))

        # Save the preferences to a different file.
        tmpdir = tempfile.mkdtemp()
        tmp = join(tmpdir, "tmp.ini")
        p.save(tmp)

        # Load the preferences again from that file.
        p = set_default_preferences(Preferences())
        p.load(tmp)

        acme_ui = AcmeUI()

        # Make some bindings.
        bind_preference(acme_ui, "bgcolor", "acme.ui.bgcolor")
        bind_preference(acme_ui, "width", "acme.ui.width")
        bind_preference(acme_ui, "ratio", "acme.ui.ratio")
        bind_preference(acme_ui, "visible", "acme.ui.visible")

        # Make sure the helper was initialized properly (with the values in
        # the .ini file *not* the trait defaults!).
        self.assertEqual("yellow", acme_ui.bgcolor)
        self.assertEqual(50, acme_ui.width)
        self.assertEqual(1.0, acme_ui.ratio)
        self.assertTrue(acme_ui.visible)

        # Clean up!
        os.remove(tmp)
        os.rmdir(tmpdir)

    def test_explicit_preferences(self):
        """ explicit preferences """

        p = self.preferences
        p.load(self.example)

        class AcmeUI(HasTraits):
            """ The Acme UI class! """

            # The traits that we want to initialize from preferences.
            bgcolor = Str
            width = Int
            ratio = Float
            visible = Bool

        acme_ui = AcmeUI()
        acme_ui.observe(listener, match(lambda n, t: True))

        # Create an empty preferences node and use that in some of the
        # bindings!
        preferences = Preferences()

        # Make some bindings.
        bind_preference(acme_ui, "bgcolor", "acme.ui.bgcolor", preferences)
        bind_preference(acme_ui, "width", "acme.ui.width")
        bind_preference(acme_ui, "ratio", "acme.ui.ratio", preferences)
        bind_preference(acme_ui, "visible", "acme.ui.visible")

        # Make sure the object was initialized properly.
        self.assertEqual("", acme_ui.bgcolor)
        self.assertEqual(50, acme_ui.width)
        self.assertEqual(0.0, acme_ui.ratio)
        self.assertTrue(acme_ui.visible)

    def test_nested_set_in_trait_change_handler(self):
        """ nested set in trait change handler """

        p = self.preferences
        p.load(self.example)

        class AcmeUI(HasTraits):
            """ The Acme UI class! """

            # The traits that we want to initialize from preferences.
            bgcolor = Str
            width = Int
            ratio = Float
            visible = Bool

            def _width_changed(self, trait_name, old, new):
                """ Static trait change handler. """

                self.ratio = 3.0

        acme_ui = AcmeUI()
        acme_ui.observe(listener, match(lambda n, t: True))

        # Make some bindings.
        bind_preference(acme_ui, "bgcolor", "acme.ui.bgcolor")
        bind_preference(acme_ui, "width", "acme.ui.width")
        bind_preference(acme_ui, "ratio", "acme.ui.ratio")
        bind_preference(acme_ui, "visible", "acme.ui.visible")

        # Make sure the object was initialized properly.
        self.assertEqual("blue", acme_ui.bgcolor)
        self.assertEqual(50, acme_ui.width)
        self.assertEqual(1.0, acme_ui.ratio)
        self.assertTrue(acme_ui.visible)

        # Change the width via the preferences node. This should cause the
        # ratio to get set via the static trait change handler on the helper.
        p.set("acme.ui.width", 42)
        self.assertEqual(42, acme_ui.width)
        self.assertEqual("42", p.get("acme.ui.width"))

        # Did the ratio get changed?
        self.assertEqual(3.0, acme_ui.ratio)
        self.assertEqual("3.0", p.get("acme.ui.ratio"))

    def test_trait_name_different_to_preference_name(self):

        p = self.preferences
        p.load(self.example)

        class AcmeUI(HasTraits):
            """ The Acme UI class! """

            # The test here is to have a different name for the trait than the
            # preference value (which is 'bgcolor').
            color = Str

        acme_ui = AcmeUI()
        acme_ui.observe(listener, match(lambda n, t: True))

        # Make some bindings.
        bind_preference(acme_ui, "color", "acme.ui.bgcolor")

        # Make sure the object was initialized properly.
        self.assertEqual("blue", acme_ui.color)

        # Change the width via the preferences node.
        p.set("acme.ui.bgcolor", "red")
        self.assertEqual("color", listener.trait_name)
        self.assertEqual("blue", listener.old)
        self.assertEqual("red", listener.new)

    def test_invalid_preference(self):

        p = self.preferences
        p.load(self.example)

        class AcmeUI(HasTraits):
            """ The Acme UI class! """

            # The traits that we want to initialize from preferences.
            invalid = Int

        acme_ui = AcmeUI()

        # Make a binding with an invalid value.
        with self.assertRaises(TraitError):
            bind_preference(acme_ui, "invalid", "acme.ui.invalid")
