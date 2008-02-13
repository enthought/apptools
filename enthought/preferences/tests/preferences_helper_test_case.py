""" Tests for the preferences helper. """


# Standard library imports.
import unittest

# Enthought library imports.
from enthought.preferences.api import Preferences, PreferencesHelper
from enthought.preferences.api import ScopedPreferences
from enthought.preferences.api import set_default_preferences
from enthought.traits.api import Bool, HasTraits, Int, Float, Str, Unicode


def listener(obj, trait_name, old, new):
    """ A useful trait change handler for testing! """
    
    listener.obj = obj
    listener.trait_name = trait_name
    listener.old = old
    listener.new = new

    return


class PreferencesHelperTestCase(unittest.TestCase):
    """ Tests for the preferences helper. """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        self.preferences = set_default_preferences(Preferences())
        
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
        p.load('example.ini')

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The path to the preferences node that contains our preferences.
            PREFERENCES_PATH = 'acme.ui'

            # The traits that we want to initialize from preferences.
            bgcolor = Str
            width   = Int
            ratio   = Float
            visible = Bool
            desc    = Unicode
            
        helper = AcmeUIPreferencesHelper()
        helper.on_trait_change(listener)

        # Make sure the helper was initialized properly.
        self.assertEqual('blue', helper.bgcolor)
        self.assertEqual(50, helper.width)
        self.assertEqual(1.0, helper.ratio)
        self.assertEqual(True, helper.visible)
        self.assertEqual(u'acme ui', helper.desc)

        # Make sure we can set the preference via the helper...
        helper.bgcolor = 'yellow'
        self.assertEqual('yellow', p.get('acme.ui.bgcolor'))
        self.assertEqual('yellow', helper.bgcolor)

        # ... and that the correct trait change event was fired.
        self.assertEqual(helper, listener.obj)
        self.assertEqual('bgcolor', listener.trait_name)
        self.assertEqual('blue', listener.old)
        self.assertEqual('yellow', listener.new)
        
        # Make sure we can set the preference via the preferences node...
        p.set('acme.ui.bgcolor', 'red') 
        self.assertEqual('red', p.get('acme.ui.bgcolor'))
        self.assertEqual('red', helper.bgcolor)

        # ... and that the correct trait change event was fired.
        self.assertEqual(helper, listener.obj)
        self.assertEqual('bgcolor', listener.trait_name)
        self.assertEqual('yellow', listener.old)
        self.assertEqual('red', listener.new)
       
        return

    def test_instance_scope_preferences_path(self):
        """ instance scope preferences path """

        p = self.preferences
        p.load('example.ini')

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The traits that we want to initialize from preferences.
            bgcolor = Str
            width   = Int
            ratio   = Float
            visible = Bool
            
        helper = AcmeUIPreferencesHelper(preferences_path='acme.ui')
        helper.on_trait_change(listener)

        # Make sure the helper was initialized properly.
        self.assertEqual('blue', helper.bgcolor)
        self.assertEqual(50, helper.width)
        self.assertEqual(1.0, helper.ratio)
        self.assertEqual(True, helper.visible)

        # Make sure we can set the preference via the helper...
        helper.bgcolor = 'yellow'
        self.assertEqual('yellow', p.get('acme.ui.bgcolor'))
        self.assertEqual('yellow', helper.bgcolor)

        # ... and that the correct trait change event was fired.
        self.assertEqual(helper, listener.obj)
        self.assertEqual('bgcolor', listener.trait_name)
        self.assertEqual('blue', listener.old)
        self.assertEqual('yellow', listener.new)
        
        # Make sure we can set the preference via the preferences node...
        p.set('acme.ui.bgcolor', 'red') 
        self.assertEqual('red', p.get('acme.ui.bgcolor'))
        self.assertEqual('red', helper.bgcolor)

        # ... and that the correct trait change event was fired.
        self.assertEqual(helper, listener.obj)
        self.assertEqual('bgcolor', listener.trait_name)
        self.assertEqual('yellow', listener.old)
        self.assertEqual('red', listener.new)

        return

    def test_default_values(self):
        """ default values """

        p = self.preferences

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The path to the preferences node that contains our preferences.
            PREFERENCES_PATH = 'acme.ui'

            # The traits that we want to initialize from preferences.
            bgcolor = Str('blue')
            width   = Int(50)
            ratio   = Float(1.0)
            visible = Bool(True)
            desc    = Unicode(u'description')
            
        helper = AcmeUIPreferencesHelper()

        # Make sure the helper was initialized properly.
        self.assertEqual('blue', helper.bgcolor)
        self.assertEqual(50, helper.width)
        self.assertEqual(1.0, helper.ratio)
        self.assertEqual(True, helper.visible)
        self.assertEqual(u'description', helper.desc)

        return

    def test_no_preferences_path(self):
        """ no preferences path """

        p = self.preferences
        p.load('example.ini')

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The traits that we want to initialize from preferences.
            bgcolor = Str
            width   = Int
            ratio   = Float
            visible = Bool

        # Cannot create a helper with a preferences path.
        self.failUnlessRaises(SystemError, AcmeUIPreferencesHelper)

        return

    def test_sync_trait(self):
        """ sync trait """

        class Widget(HasTraits):
            """ A widget! """

            background_color = Str

        w = Widget()
        w.on_trait_change(listener)

        p = self.preferences
        p.load('example.ini')

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The path to the preferences node that contains our preferences.
            PREFERENCES_PATH = 'acme.ui'

            # The traits that we want to initialize from preferences.
            bgcolor = Str
            width   = Int
            ratio   = Float
            visible = Bool

        helper = AcmeUIPreferencesHelper()
        helper.sync_trait('bgcolor', w, 'background_color')

        # Make sure the helper was initialized properly.
        self.assertEqual('blue', helper.bgcolor)
        self.assertEqual(50, helper.width)
        self.assertEqual(1.0, helper.ratio)
        self.assertEqual(True, helper.visible)

        self.assertEqual('blue', w.background_color)

        # Make sure we can set the preference via the helper...
        helper.bgcolor = 'yellow'
        self.assertEqual('yellow', p.get('acme.ui.bgcolor'))
        self.assertEqual('yellow', helper.bgcolor)

        self.assertEqual('yellow', w.background_color)

        # ... and that the correct trait change event was fired.
        self.assertEqual(w, listener.obj)
        self.assertEqual('background_color', listener.trait_name)
        self.assertEqual('blue', listener.old)
        self.assertEqual('yellow', listener.new)
        
        # Make sure we can set the preference via the preferences node...
        p.set('acme.ui.bgcolor', 'red') 
        self.assertEqual('red', p.get('acme.ui.bgcolor'))
        self.assertEqual('red', helper.bgcolor)

        self.assertEqual('red', w.background_color)

        # ... and that the correct trait change event was fired.
        self.assertEqual(w, listener.obj)
        self.assertEqual('background_color', listener.trait_name)
        self.assertEqual('yellow', listener.old)
        self.assertEqual('red', listener.new)

        return

    def test_scoped_preferences(self):
        """ scoped preferences """

        p = set_default_preferences(ScopedPreferences())

        # Set a preference value in the default scope.
        p.set('default/acme.ui.bgcolor', 'blue')

        class AcmeUIPreferencesHelper(PreferencesHelper):
            """ A helper! """

            # The path to the preferences node that contains our preferences.
            PREFERENCES_PATH = 'acme.ui'

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
            PREFERENCES_PATH = 'acme.ui'

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


# Entry point for stand-alone testing.
if __name__ == '__main__':
    unittest.main()

#### EOF ######################################################################
