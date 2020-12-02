# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" An example of using the preferences manager. """


# Enthought library imports.
from traits.api import Color, Int
from traitsui.api import View

# Local imports.
from apptools.preferences.api import Preferences
from apptools.preferences.api import get_default_preferences
from apptools.preferences.api import set_default_preferences
from apptools.preferences.ui.api import PreferencesManager, PreferencesPage


# Create a preferences collection from a file and make it the default root
# preferences node for all preferences helpers etc.
set_default_preferences(Preferences(filename='example.ini'))


class AcmePreferencesPage(PreferencesPage):
    """ A preference page for the Acme preferences. """

    #### 'IPreferencesPage' interface #########################################

    # The page's category (e.g. 'General/Appearence'). The empty string means
    # that this is a top-level page.
    category = ''

    # The page's help identifier (optional). If a help Id *is* provided then
    # there will be a 'Help' button shown on the preference page.
    help_id = ''

    # The page name (this is what is shown in the preferences dialog.
    name = 'Acme'

    # The path to the preferences node that contains our preferences.
    preferences_path = 'acme'

    #### Preferences ##########################################################

    width = Int(800)
    height = Int(600)

    #### Traits UI views ######################################################

    view = View('width', 'height')


class AcmeWorkbenchPreferencesPage(PreferencesPage):
    """ A preference page for the Acme workbench preferences. """

    #### 'IPreferencesPage' interface #########################################

    # The page's category (e.g. 'General/Appearence'). The empty string means
    # that this is a top-level page.
    category = 'Acme'

    # The page's help identifier (optional). If a help Id *is* provided then
    # there will be a 'Help' button shown on the preference page.
    help_id = ''

    # The page name (this is what is shown in the preferences dialog.
    name = 'Workbench'

    # The path to the preferences node that contains our preferences.
    preferences_path = 'acme'

    #### Preferences ##########################################################

    bgcolor = Color
    fgcolor = Color

    #### Traits UI views ######################################################

    view = View('bgcolor', 'fgcolor')


# Entry point.
if __name__ == '__main__':

    # Create a manager with some pages.
    preferences_manager = PreferencesManager(
        pages=[AcmePreferencesPage(), AcmeWorkbenchPreferencesPage()]
    )

    # Show the UI...
    preferences_manager.configure_traits()

    # Save the preferences...
    get_default_preferences().flush()
