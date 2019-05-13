""" Defines classes for preferences pages for the help plugin.

    :Copyright: 2008, Enthought Inc.
    :License: BSD
    :Author: Janet Swisher
"""
# This software is provided without warranty under the terms of the BSD
# license included in AppTools/trunk/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!

from apptools.preferences.ui.api import PreferencesPage
from traits.api import Either, File, Str
from traitsui.api import Group, Item, Label, View

# This module's package.
PKG = '.'.join(__name__.split('.')[:-1])

class HelpPreferencesPage(PreferencesPage):
    """ Base class for root preference pages for the help plugin.
    """
    #### 'PreferencesPage' interface ##########################################

    # The page's category (e.g. 'General/Appearance'). The empty string means
    # that this is a top-level page.
    category = ''

    # The page's help identifier (optional). If a help ID *is* provided then
    # there will be a 'Help' button shown on the preference page.
    help_id = ''

    # The page name (this is what is shown in the preferences dialog.
    name = 'Help'

    # The path to the preferences node that contains the preferences.
    preferences_path = PKG

    traits_view = View()

class DocumentsPreferencesPage(HelpPreferencesPage):
    """ (Blank) page for the "Documents" preferences tree node.
    """
    name = 'Documents'

class DemosPreferencesPage(HelpPreferencesPage):
    """ (Blank) page for the "Demos" preferences tree node.
    """
    name = 'Demos'

class ExamplesPreferencesPage(HelpPreferencesPage):
    """ Page for the "Examples" preferences tree node.
    """
    name = 'Examples'
    preferences_path = PKG + '.Examples'

    #### Preferences ###########################################################

    editor = Str

    traits_view = View(
        Item( name='editor',
              label='Command for external editor'),
    )

class HelpDocPreferencesPage(PreferencesPage):
    """ Base class for preferences pages for help documents.
    """
    #### 'PreferencesPage' interface ##########################################

    # The page's category.
    category = 'Documents'

    # The page's help identifier (optional).
    help_id = ''

    # The page name (this is what is shown in the preferences dialog.
    name = Str

    def _name_default(self):
        return self.label

    # The path to the preferences node that contains the preferences.
    preferences_path = Str

    #### Preferences ###########################################################

    # The UI label for the help doc, which appears in menus or dialogs.
    label = Str

    # The full path to the document on disk.
    filename = File

    # The program to use to view the document. 'browser' means the platform
    # default web browser.
    viewer = Either('browser', File)

    traits_view = View(
        Group(
            Item('viewer', show_label=True),
            Label("Viewer can be 'browser' or a path to a program."),
            show_border=True,
        ),
            Item('filename', show_label=True),
            Label("Filename can be absolute, or relative to the Python directory."),

    )

class HelpDemoPreferencesPage(PreferencesPage):
    """ Base class for preferences pages for help demos.
    """
    #### 'PreferencesPage' interface ##########################################

    # The page's category (e.g. 'General/Appearance'). The empty string means
    # that this is a top-level page.
    category = 'Demos'

    # The page's help identifier (optional). If a help ID *is* provided then
    # there will be a 'Help' button shown on the preference page.
    help_id = ''

    # The page name (this is what is shown in the preferences dialog.
    name = Str

    def _name_default(self):
        return self.label

    # The path to the preferences node that contains the preferences.
    preferences_path = Str

    #### Preferences ###########################################################

    # The UI label for the help demo, which appears in menus or dialogs.
    label = Str

    # The full path to entry point for the demo.
    filename = File

    traits_view = View(
        Item('filename', show_label=True),
        Label("Filename can be absolute, or relative to the Python directory."),
    )


class HelpExamplePreferencesPage(PreferencesPage):
    """ Base class for preferences pages for help examples.
    """
    #### 'PreferencesPage' interface ##########################################

    # The page's category (e.g. 'General/Appearance'). The empty string means
    # that this is a top-level page.
    category = 'Examples'

    # The page's help identifier (optional). If a help ID *is* provided then
    # there will be a 'Help' button shown on the preference page.
    help_id = ''

    # The page name (this is what is shown in the preferences dialog.
    name = Str

    def _name_default(self):
        return self.label

    # The path to the preferences node that contains the preferences.
    preferences_path = Str

    #### Preferences ###########################################################

    # The UI label for the help demo, which appears in menus or dialogs.
    label = Str

    # The full path to the main file of the example.
    filename = File

    traits_view = View(
        Item('filename', show_label=True),
        Label("Filename can be absolute, or relative to the Python directory."),
    )

#### EOF ######################################################################
