""" Tests for the preferences page. """

import unittest

from traits.api import Enum, List, Str
from traitsui.api import Group, Item, View

from apptools.preferences.api import Preferences
from apptools.preferences.ui.api import PreferencesPage


class TestPreferencesPage(unittest.TestCase):
    """ Non-GUI Tests for PreferencesPage."""

    def test_preferences_page_apply(self):
        """ Test applying the preferences """

        # this sets up imitate Mayavi usage.

        class MyPreferencesPage(PreferencesPage):

            # the following set default values for class traits
            category = "Application"

            help_id = ""

            name = "Note"

            preferences_path = "my_ref.pref"

            # custom preferences

            backend = Enum("auto", "simple", "test")

            traits_view = View(Group(Item("backend")))

        preferences = Preferences()
        pref_page = MyPreferencesPage(
            preferences=preferences,
            category="Another Application",
            help_id="this_wont_be_saved",
            name="Different Note",
            # custom preferences
            backend="simple",
        )
        pref_page.apply()

        self.assertEqual(preferences.get("my_ref.pref.backend"), "simple")
        self.assertEqual(preferences.keys("my_ref.pref"), ["backend"])

        # this is not saved by virtue of it being static and never assigned to
        self.assertIsNone(preferences.get("my_ref.pref.traits_view"))

        # These are skipped because this trait is defined on the
        # PreferencesPage.
        self.assertIsNone(preferences.get("my_ref.pref.help_id"))
        self.assertIsNone(preferences.get("my_ref.pref.category"))
        self.assertIsNone(preferences.get("my_ref.pref.name"))

    def test_preferences_page_apply_skip_items_traits(self):
        """ Test _items traits from List mutation are skipped. """
        # Regression test for enthought/apptools#129

        class MyPreferencesPage(PreferencesPage):
            preferences_path = "my_ref.pref"
            names = List(Str())

        preferences = Preferences()
        pref_page = MyPreferencesPage(
            preferences=preferences,
            names=["1"],
        )
        pref_page.names.append("2")
        pref_page.apply()

        self.assertEqual(preferences.keys("my_ref.pref"), ["names"])
