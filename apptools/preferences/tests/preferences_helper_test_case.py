""" Tests for the preferences helper. """


# Standard library imports.
import time
import unittest

# Major package imports.
from pkg_resources import resource_filename

# Enthought library imports.
from apptools.preferences.api import Preferences, PreferencesHelper
from apptools.preferences.api import ScopedPreferences
from apptools.preferences.api import set_default_preferences
from traits.api import Any, Bool, HasTraits, Int, Float, List, Str, Unicode


def width_listener(obj, trait_name, old, new):

    width_listener.obj = obj
    width_listener.trait_name = trait_name
    width_listener.old = old
    width_listener.new = new

    return


def bgcolor_listener(obj, trait_name, old, new):

    bgcolor_listener.obj = obj
    bgcolor_listener.trait_name = trait_name
    bgcolor_listener.old = old
    bgcolor_listener.new = new

    return

# This module's package.
PKG = 'apptools.preferences.tests'


class PreferencesHelperTestCase(unittest.TestCase):
    """ Tests for the preferences helper. """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        self.preferences = set_default_preferences(Preferences())

        # The filename of the example preferences file.
        self.example = resource_filename(PKG, 'example.ini')

        return

    def tearDown(self):
        """ Called immediately after each test method has been called. """

        return

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
            preferences_path = 'acme.ui'

            # The traits that we want to initialize from preferences.
            bgcolor     = Str
            width       = Int
            ratio       = Float
            visible     = Bool
            description = Unicode
            offsets     = List(Int)
            names       = List(Str)

        helper = AcmeUIPreferencesHelper()
        helper.on_trait_change(bgcolor_listener)

        # Make sure the helper was initialized properly.
        self.assertEqual('blue', helper.bgcolor)
        self.assertEqual(50, helper.width)
        self.assertEqual(1.0, helper.ratio)
        self.assertEqual(True, helper.visible)
        self.assertEqual(u'acme ui', helper.description)
        self.assertEqual([1, 2, 3, 4], helper.offsets)
        self.assertEqual(['joe', 'fred', 'jane'], helper.names)

        # Make sure we can set the preference via the helper...
        helper.bgcolor = 'yellow'
        self.assertEqual('yellow', p.get('acme.ui.bgcolor'))
        self.assertEqual('yellow', helper.bgcolor)

        # ... and that the correct trait change event was fired.
        self.assertEqual(helper, bgcolor_listener.obj)
        self.assertEqual('bgcolor', bgcolor_listener.trait_name)
        self.assertEqual('blue', bgcolor_listener.old)
        self.assertEqual('yellow', bgcolor_listener.new)

        # Make sure we can set the preference via the preferences node...
        p.set('acme.ui.bgcolor', 'red')
        self.assertEqual('red', p.get('acme.ui.bgcolor'))
        self.assertEqual('red', helper.bgcolor)

        # ... and that the correct trait change event was fired.
        self.assertEqual(helper, bgcolor_listener.obj)
        self.assertEqual('bgcolor', bgcolor_listener.trait_name)
        self.assertEqual('yellow', bgcolor_listener.old)
        self.assertEqual('red', bgcolor_listener.new)

        return

    def test_instance_scope_preferences_path(self):
        """ instance scope preferences path """

        p = self.preferences
        p.load(self.example)

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The traits that we want to initialize from preferences.
            bgcolor     = Str
            width       = Int
            ratio       = Float
            visible     = Bool
            description = Unicode
            offsets     = List(Int)
            names       = List(Str)

        helper = AcmeUIPreferencesHelper(preferences_path='acme.ui')
        helper.on_trait_change(bgcolor_listener)

        # Make sure the helper was initialized properly.
        self.assertEqual('blue', helper.bgcolor)
        self.assertEqual(50, helper.width)
        self.assertEqual(1.0, helper.ratio)
        self.assertEqual(True, helper.visible)
        self.assertEqual(u'acme ui', helper.description)
        self.assertEqual([1, 2, 3, 4], helper.offsets)
        self.assertEqual(['joe', 'fred', 'jane'], helper.names)

        # Make sure we can set the preference via the helper...
        helper.bgcolor = 'yellow'
        self.assertEqual('yellow', p.get('acme.ui.bgcolor'))
        self.assertEqual('yellow', helper.bgcolor)

        # ... and that the correct trait change event was fired.
        self.assertEqual(helper, bgcolor_listener.obj)
        self.assertEqual('bgcolor', bgcolor_listener.trait_name)
        self.assertEqual('blue', bgcolor_listener.old)
        self.assertEqual('yellow', bgcolor_listener.new)

        # Make sure we can set the preference via the preferences node...
        p.set('acme.ui.bgcolor', 'red')
        self.assertEqual('red', p.get('acme.ui.bgcolor'))
        self.assertEqual('red', helper.bgcolor)

        # ... and that the correct trait change event was fired.
        self.assertEqual(helper, bgcolor_listener.obj)
        self.assertEqual('bgcolor', bgcolor_listener.trait_name)
        self.assertEqual('yellow', bgcolor_listener.old)
        self.assertEqual('red', bgcolor_listener.new)

        return

    def test_default_values(self):
        """ default values """

        p = self.preferences

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The path to the preferences node that contains our preferences.
            preferences_path = 'acme.ui'

            # The traits that we want to initialize from preferences.
            bgcolor     = Str('blue')
            width       = Int(50)
            ratio       = Float(1.0)
            visible     = Bool(True)
            description = Unicode(u'description')
            offsets     = List(Int, [1, 2, 3, 4])
            names       = List(Str, ['joe', 'fred', 'jane'])

        helper = AcmeUIPreferencesHelper()

        # Make sure the helper was initialized properly.
        self.assertEqual('blue', helper.bgcolor)
        self.assertEqual(50, helper.width)
        self.assertEqual(1.0, helper.ratio)
        self.assertEqual(True, helper.visible)
        self.assertEqual(u'description', helper.description)
        self.assertEqual([1, 2, 3, 4], helper.offsets)
        self.assertEqual(['joe', 'fred', 'jane'], helper.names)

        return

    def test_real_unicode_values(self):
        """ Test with real life unicode values """

        p = self.preferences
        p.load(self.example)

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The path to the preferences node that contains our preferences.
            preferences_path = 'acme.ui'

            # The traits that we want to initialize from preferences.
            bgcolor     = Str('blue')
            width       = Int(50)
            ratio       = Float(1.0)
            visible     = Bool(True)
            description = Unicode(u'')
            offsets     = List(Int, [1, 2, 3, 4])
            names       = List(Str, ['joe', 'fred', 'jane'])

        helper = AcmeUIPreferencesHelper()

        first_unicode_str = u'U\xdc\xf2ser'
        first_utf8_str = 'U\xc3\x9c\xc3\xb2ser'

        original_description = helper.description
        helper.description = first_unicode_str
        self.assertEqual(first_unicode_str, helper.description)


        second_unicode_str = u'caf\xe9'
        second_utf8_str = 'caf\xc3\xa9'
        helper.description = second_unicode_str
        self.assertEqual(second_unicode_str, helper.description)
        self.assertEqual(second_unicode_str, p.get('acme.ui.description'))

        p.save(self.example)

        p.load(self.example)
        self.assertEqual(second_unicode_str, p.get('acme.ui.description'))
        self.assertEqual(u'True', p.get('acme.ui.visible'))
        self.assertEqual(True, helper.visible)

        # reset the original description and save the example file
        helper.description = original_description
        p.save(self.example)

    def test_no_preferences_path(self):
        """ no preferences path """

        p = self.preferences
        p.load(self.example)

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The traits that we want to initialize from preferences.
            bgcolor     = Str
            width       = Int
            ratio       = Float
            visible     = Bool
            description = Unicode
            offsets     = List(Int)
            names       = List(Str)

        # Cannot create a helper with a preferences path.
        self.assertRaises(SystemError, AcmeUIPreferencesHelper)

        return

    def test_sync_trait(self):
        """ sync trait """

        class Widget(HasTraits):
            """ A widget! """

            background_color = Str

        w = Widget()
        w.on_trait_change(bgcolor_listener)

        p = self.preferences
        p.load(self.example)

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The path to the preferences node that contains our preferences.
            preferences_path = 'acme.ui'

            # The traits that we want to initialize from preferences.
            bgcolor     = Str
            width       = Int
            ratio       = Float
            visible     = Bool
            description = Unicode
            offsets     = List(Int)
            names       = List(Str)

        helper = AcmeUIPreferencesHelper()
        helper.sync_trait('bgcolor', w, 'background_color')

        # Make sure the helper was initialized properly.
        self.assertEqual('blue', helper.bgcolor)
        self.assertEqual(50, helper.width)
        self.assertEqual(1.0, helper.ratio)
        self.assertEqual(True, helper.visible)
        self.assertEqual(u'acme ui', helper.description)
        self.assertEqual([1, 2, 3, 4], helper.offsets)
        self.assertEqual(['joe', 'fred', 'jane'], helper.names)

        self.assertEqual('blue', w.background_color)

        # Make sure we can set the preference via the helper...
        helper.bgcolor = 'yellow'
        self.assertEqual('yellow', p.get('acme.ui.bgcolor'))
        self.assertEqual('yellow', helper.bgcolor)

        self.assertEqual('yellow', w.background_color)

        # ... and that the correct trait change event was fired.
        self.assertEqual(w, bgcolor_listener.obj)
        self.assertEqual('background_color', bgcolor_listener.trait_name)
        self.assertEqual('blue', bgcolor_listener.old)
        self.assertEqual('yellow', bgcolor_listener.new)

        # Make sure we can set the preference via the preferences node...
        p.set('acme.ui.bgcolor', 'red')
        self.assertEqual('red', p.get('acme.ui.bgcolor'))
        self.assertEqual('red', helper.bgcolor)

        self.assertEqual('red', w.background_color)

        # ... and that the correct trait change event was fired.
        self.assertEqual(w, bgcolor_listener.obj)
        self.assertEqual('background_color', bgcolor_listener.trait_name)
        self.assertEqual('yellow', bgcolor_listener.old)
        self.assertEqual('red', bgcolor_listener.new)

        return

    def test_scoped_preferences(self):
        """ scoped preferences """

        p = set_default_preferences(ScopedPreferences())

        # Set a preference value in the default scope.
        p.set('default/acme.ui.bgcolor', 'blue')

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The path to the preferences node that contains our preferences.
            preferences_path = 'acme.ui'

            # The traits that we want to initialize from preferences.
            bgcolor = Str

            # A trait for a preference that does not exist yet.
            name = Str

        helper = AcmeUIPreferencesHelper()

        # Make sure the trait is set!
        self.assertEqual('blue', helper.bgcolor)

        # And that the non-existent trait gets the default value.
        self.assertEqual('', helper.name)

        return

    def test_preference_not_in_file(self):
        """ preference not in file """

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The path to the preferences node that contains our preferences.
            preferences_path = 'acme.ui'

            # A trait that has no corresponding value in the file.
            title = Str('Acme')

        helper = AcmeUIPreferencesHelper()

        # Make sure the trait is set!
        self.assertEqual('Acme', helper.title)

        # Set a new value.
        helper.title = 'Acme Plus'

        # Make sure the trait is set!
        self.assertEqual('Acme Plus', helper.title)
        self.assertEqual('Acme Plus', self.preferences.get('acme.ui.title'))

        return

    def test_preferences_node_changed(self):
        """ preferences node changed """

        p = self.preferences
        p.load(self.example)

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The path to the preferences node that contains our preferences.
            preferences_path = 'acme.ui'

            # The traits that we want to initialize from preferences.
            bgcolor     = Str
            width       = Int
            ratio       = Float
            visible     = Bool
            description = Unicode
            offsets     = List(Int)
            names       = List(Str)

        helper = AcmeUIPreferencesHelper()

        # We only listen to some of the traits so the testing is easier.
        helper.on_trait_change(width_listener, ['width'])
        helper.on_trait_change(bgcolor_listener, ['bgcolor'])

        # Create a new preference node.
        p1 = Preferences()
        p1.load(self.example)

        p1.set('acme.ui.bgcolor', 'red')
        p1.set('acme.ui.width', 40)

        # Set the new preferences
        helper.preferences = p1

        # Test event handling.
        self.assertEqual(helper, width_listener.obj)
        self.assertEqual('width', width_listener.trait_name)
        self.assertEqual(50, width_listener.old)
        self.assertEqual(40, width_listener.new)

        self.assertEqual(helper, bgcolor_listener.obj)
        self.assertEqual('bgcolor', bgcolor_listener.trait_name)
        self.assertEqual('blue', bgcolor_listener.old)
        self.assertEqual('red', bgcolor_listener.new)

        # Test re-initialization.
        self.assertEqual(helper.bgcolor, 'red')
        self.assertEqual(helper.width, 40)

        # Test event handling.
        p1.set('acme.ui.bgcolor', 'black')
        self.assertEqual(helper, bgcolor_listener.obj)
        self.assertEqual('bgcolor', bgcolor_listener.trait_name)
        self.assertEqual('red', bgcolor_listener.old)
        self.assertEqual('black', bgcolor_listener.new)

        # This should not trigger any new changes since we are setting values
        # on the old preferences node.
        p.set('acme.ui.bgcolor', 'white')
        self.assertEqual(helper, bgcolor_listener.obj)
        self.assertEqual('bgcolor', bgcolor_listener.trait_name)
        self.assertEqual('red', bgcolor_listener.old)
        self.assertEqual('black', bgcolor_listener.new)

        return

    def test_nested_set_in_trait_change_handler(self):
        """ nested set in trait change handler """

        p = self.preferences
        p.load(self.example)

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The traits that we want to initialize from preferences.
            bgcolor     = Str
            width       = Int
            ratio       = Float
            visible     = Bool
            description = Unicode
            offsets     = List(Int)
            names       = List(Str)

            # When the width changes, change the ratio.
            def _width_changed(self, trait_name, old, new):
                """ Static trait change handler. """

                self.ratio = 3.0

                return

        helper = AcmeUIPreferencesHelper(preferences_path='acme.ui')

        # Make sure the helper was initialized properly.
        self.assertEqual('blue', helper.bgcolor)
        self.assertEqual(50, helper.width)
        self.assertEqual(1.0, helper.ratio)
        self.assertEqual(True, helper.visible)
        self.assertEqual(u'acme ui', helper.description)
        self.assertEqual([1, 2, 3, 4], helper.offsets)
        self.assertEqual(['joe', 'fred', 'jane'], helper.names)

        # Change the width via the preferences node. This should cause the
        # ratio to get set via the static trait change handler on the helper.
        p.set('acme.ui.width', 42)
        self.assertEqual(42, helper.width)
        self.assertEqual('42', p.get('acme.ui.width'))

        # Did the ratio get changed?
        self.assertEqual(3.0, helper.ratio)
        self.assertEqual('3.0', p.get('acme.ui.ratio'))

        return

    # fixme: No comments - nice work... I added the doc string and the 'return'
    # to be compatible with the rest of the module. Interns please note correct
    # procedure when modifying existing code. If in doubt, ask a developer.
    def test_unevaluated_strings(self):
        """ unevaluated strings """

        p = self.preferences
        p.load(self.example)

        class AcmeUIPreferencesHelper(PreferencesHelper):
            width = Any(is_str=True)

        helper = AcmeUIPreferencesHelper(preferences_path='acme.ui')

        self.assertEqual('50', helper.width)

        return


# Entry point for stand-alone testing.
if __name__ == '__main__':
    unittest.main()

#### EOF ######################################################################
