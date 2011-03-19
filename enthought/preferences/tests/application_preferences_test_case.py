""" Tests for the application preferences. """


import unittest

from skeleton.preferences.application_preferences import ApplicationPreferences


class ApplicationPreferencesTestCase(unittest.TestCase):
    """ Tests for the application preferences.

    You'll notice that there aren't many tests here, since all the
    'ApplicationPreferences' class does is change the default scopes that it
    provides. Hence, the rest of its functionality is tested in the tests
    for 'ScopedPreferences'.

    """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        return

    def tearDown(self):
        """ Called immediately after each test method has been called. """

        return

    ###########################################################################
    # Tests.
    ###########################################################################

    def test_builtin_scopes(self):

        preferences = ApplicationPreferences()

        self.assertEqual(
            ['command-line', 'user', 'default'],
            [scope.name for scope in preferences.scopes]
         )

        return


# Entry point for stand-alone testing.
if __name__ == '__main__':
    unittest.main()

#### EOF ######################################################################
