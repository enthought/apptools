# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Tests for the preferences page. """

import unittest

from traits.api import (
    Enum, List, Str,
    pop_exception_handler,
    push_exception_handler,
)

from apptools.preferences.api import Preferences
from apptools._testing.optional_dependencies import requires_traitsui, traitsui

if traitsui is not None:
    from traitsui.api import Group, Item, View
    from apptools.preferences.ui.api import PreferencesPage


@requires_traitsui
class TestPreferencesPage(unittest.TestCase):
    """ Non-GUI Tests for PreferencesPage."""

    def setUp(self):
        push_exception_handler(reraise_exceptions=True)
        self.addCleanup(pop_exception_handler)

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

        self.assertEqual(preferences.get("my_ref.pref.names"), str(["1", "2"]))
        self.assertEqual(preferences.keys("my_ref.pref"), ["names"])

    def test_sync_anytrait_items_overload(self):
        """ Test sychronizing trait with name *_items not to be mistaken
        as the event trait for mutating list/dict/set
        """

        class MyPreferencesPage(PreferencesPage):
            preferences_path = Str('my_section')

            names_items = Str()

        preferences = Preferences()
        pref_page = MyPreferencesPage(preferences=preferences)
        pref_page.names_items = "Hello"
        pref_page.apply()

        self.assertEqual(
            sorted(preferences.keys("my_section")),
            ["names_items"]
        )
        self.assertEqual(
            preferences.get("my_section.names_items"),
            "Hello",
        )
