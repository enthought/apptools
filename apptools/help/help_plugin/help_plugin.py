""" The definition of an Envisage plugin for online help.

It assumes that the Workbench plugin is being used.

    :Copyright: 2008, Enthought Inc.
    :License: BSD
    :Author: Janet Swisher
"""
# This software is provided without warranty under the terms of the BSD
# license included in AppTools/trunk/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!

# Standard library imports.
import logging
import new

# Enthought libary imports
from envisage.api import Plugin, ExtensionPoint
from envisage.ui.action.api import ActionSet, Group, Menu
from traits.api import Instance, List, Str

# Local imports
from .help_code import HelpCode
from .help_doc import HelpDoc
from .i_help_code import IHelpCode
from .i_help_doc import IHelpDoc

# Logging.
logger = logging.getLogger(__name__)

HELP_MENU = 'MenuBar/Help'
DOCS_MENU = 'Documents'
DOCS_GROUP = 'DocsGroup'
DEMOS_MENU = 'Demos'
DEMOS_GROUP = 'DemosGroup'
EXAMPLES_MENU = 'Examples'
EXAMPLES_GROUP = 'ExamplesGroup'
DOWNLOADS_MENU = 'Downloads'

# This module's package.
PKG = '.'.join(__name__.split('.')[:-1])


################################################################################
# The plugin
################################################################################
class HelpPlugin(Plugin):
    """ A Help plugin for Envisage Workbench applications.

    This plugin displays items on the Workbench Help menu, based on
    contributions from itself or other plugins.
    """
    # IDs of extension points this plugin offers.
    HELP_DOCS = PKG + '.help_docs'
    HELP_DEMOS = PKG + '.help_demos'
    HELP_EXAMPLES = PKG + '.help_examples'
    HELP_DOWNLOADS = PKG + '.help_downloads'

    # IDs of extension points this plugin contributes to.
    WORKBENCH_ACTION_SETS='envisage.ui.workbench.action_sets'
    PREFERENCES       = 'envisage.preferences'
    PREFERENCES_PAGES = 'envisage.ui.workbench.preferences_pages'

    #### 'IPlugin' interface ##################################################

    # The plugin's unique identifier.
    id = 'apptools.help.help_plugin'

    # The plugin's name (suitable for displaying to the user).
    name = 'Help Plugin'

    #### public 'HelpPlugin' interface ########################################

    # List of menu names added to the main toolbar by this plugin
    # (These are placed before the 'Help' Menu).
    menus = List(Str)

    #### Extension points offered by this plugin ##############################

    help_docs = ExtensionPoint(
        List(IHelpDoc), id=HELP_DOCS, desc="""

        A help doc is defined by a preference node that specifies a UI label,
        a filename for the document, and a (path to a) viewer for viewing the
        document.

        Each contribution to this extension point must be an instance of a
        class that implements IHelpDoc. The easiest way to do this is to
        create an instance of  `apptools.help.help_plugin.api.HelpDoc`.

        So, to contribute a help doc:

        1. Create a preferences file for your plugin if it doesn't already
           have one. (Be sure to contribute your preferences file to the
           `envisage.preferences` extension point.)

        2. Define a unique "node" (section heading) in your preferences file
           for each document, and specify values for the 'label', 'viewer',
           and 'filename' settings. (Use 'browser' as the value of 'viewer' if
           the document can be viewed in a web browser.)

        3. For each document, contribute a HelpDoc to this extension point,
           and specify its *preferences_path* as the corresponding node
           name from your preferences file.
        """
    )

    help_demos = ExtensionPoint(
        List(IHelpCode), id=HELP_DEMOS, desc="""

        A help demo is a Python program that is run when it is selected from
        the Help>Demos submenu. It is defined by a preference node that
        specifies a UI label and a filename for the demo entry point.

        Each contribution to this extension point must be an instance of a
        class that implements IHelpCode. The easiest way to do this is to
        create an instance of  `apptools.help.help_plugin.api.HelpCode`.

        So, to contribute a help demo:

        1. Create a preferences file for your plugin if it doesn't already
           have one. (Be sure to contribute your preferences file to the
           `envisage.preferences` extension point.)

        2. Define a unique "node" (section heading) in your preferences file
           for each demo, and specify values for the 'label' and 'filename'
           settings. (Note that the same preferences section can be used for
           a help demo and a help example.)

        3. For each demo, contribute a HelpDemo to this extension point,
           and specify its *preferences_path* as the corresponding node
           name from your preferences file.
        """
    )

    help_examples = ExtensionPoint(
        List(IHelpCode), id=HELP_EXAMPLES, desc="""

        A help example is a Python file that is opened for viewing when it is
        selected from the Help>Examples submenu. It is defined by a preference
        node that specifies a UI label and a filename for the primary example
        file.

        Each contribution to this extension point must be an instance of a
        class that implements IHelpCode. The easiest way to do this is to
        create an instance of `apptools.help.help_plugin.api.HelpCode`.

        So, to contribute a help example:

        1. Create a preferences file for your plugin if it doesn't already
           have one. (Be sure to contribute your preferences file to the
           `envisage.preferences` extension point.)

        2. Define a unique "node" (section heading) in your preferences file
           for each example, and specify values for the 'label' and 'filename'
           settings. (Note that the same preferences section can be used for
           a help demo and a help example.)

        3. For each example, contribute a HelpCode to this extension point,
           and specify its *preferences_path* as the corresponding node
           name from your preferences file.
        """
    )

    help_downloads = ExtensionPoint(
        List(IHelpDoc), id=HELP_DOWNLOADS, desc="""

        A help download is a url that is opened in a browser for viewing when it
        is selected from the Help>Downloads submenu. It is defined by a
        preference node that specifies a UI label and a url for the download.

        Each contribution to this extension point must be an instance of a
        class that implements IHelpDoc, and has the url trait set to True. The
        easiest way to do this is to create an instance of
        `apptools.help.help_plugin.api.HelpDoc`.

        So, to contribute a help doc:

        1. Create a preferences file for your plugin if it doesn't already
           have one. (Be sure to contribute your preferences file to the
           `envisage.preferences` extension point.)

        2. Define a unique "node" (section heading) in your preferences file
           for each url, and specify values for the 'label' and 'filename'
           settings. Also set 'url' to True.

        3. For each document, contribute a HelpDoc to this extension point,
           and specify its *preferences_path* as the corresponding node
           name from your preferences file.
        """
    )

    # FIXME: Ideally, there should be an extension point to allow plugins to
    #        offer editors to display examples (e.g., TextEditorPlugin or
    #        RemoteEditorPlugin). For now, examples open in an external editor
    #        launched with subprocess.Popen. The user can set the editor
    #        command in the Examples preferences page.


    ###### Contributions to extension points made by this plugin ######

    help_action_sets = List(contributes_to=WORKBENCH_ACTION_SETS)
    def _help_action_sets_default(self):
        """ Returns a list containing an action set class whose **actions**
            correspond to the help docs in the help_docs extension point.
        """
        extension_point_mapping = {
                                DOCS_MENU: self.help_docs,
                                EXAMPLES_MENU: self.help_examples,
                                DEMOS_MENU: self.help_demos,
                                DOWNLOADS_MENU: self.help_downloads}

        # Construct traits for the action set
        ns = {'id': 'apptools.help.help_plugin.help_action_set',
              'name': 'Help Plugin ActionSet',
              'groups': [ Group( id=DOCS_GROUP, before='AboutGroup',
                                 path=HELP_MENU ) ]
              }

        for (menu_name, items) in extension_point_mapping.items():
            if len(items) > 0:
                menu = Menu( name = menu_name,
                             class_name =
                             PKG + '.help_submenu_manager:%sMenuManager' %
                             menu_name )
                if menu_name in self.menus:
                    menu.path = 'MenuBar'
                    menu.before = 'Help'
                else:
                    menu.path = HELP_MENU
                    menu.group = DOCS_GROUP

                # Append the menu.
                ns.setdefault('menus', []).append(menu)

        return [new.classobj('SPLHelpActionSet', (ActionSet,), ns)]

    preferences = List(contributes_to=PREFERENCES)
    def _preferences_default(self):
        return ['pkgfile://%s/preferences.ini' % PKG]

    preferences_pages = List(contributes_to=PREFERENCES_PAGES)
    def _preferences_pages_default(self):
        from apptools.help.help_plugin.preferences_pages import \
            DocumentsPreferencesPage, DemosPreferencesPage, \
            ExamplesPreferencesPage, HelpDocPreferencesPage, \
            HelpDemoPreferencesPage, HelpExamplePreferencesPage
        pages = []
        if len(self.help_docs) > 0:
            pages.append(DocumentsPreferencesPage)
            pages.extend(
                [ new.classobj(doc.preferences_path + 'PreferencesPage',
                              (HelpDocPreferencesPage,),
                              {'preferences_path': doc.preferences_path},
                             ) for doc in self.help_docs
                ])
        if len(self.help_demos) > 0:
            pages.append(DemosPreferencesPage)
            pages.extend(
                [ new.classobj(demo.preferences_path + 'PreferencesPage',
                              (HelpDemoPreferencesPage,),
                              {'preferences_path': demo.preferences_path},
                             ) for demo in self.help_demos
                ])
        if len(self.help_examples) > 0:
            pages.append(ExamplesPreferencesPage)
            pages.extend(
                [ new.classobj(example.preferences_path + 'PreferencesPage',
                              (HelpExamplePreferencesPage,),
                              {'preferences_path': example.preferences_path},
                             ) for example in self.help_examples
                ])
        return pages

    #my_help_demos = List(contributes_to=HELP_DEMOS)
    #def _my_help_demos_default(self):
    #    return [HelpCode( preferences_path=PKG + '.TraitsDemo'),
    #           ]

    #my_help_examples = List(contributes_to=HELP_EXAMPLES)
    #def _my_help_examples_default(self):
    #    return [HelpCode( preferences_path=PKG + '.AcmeLab'),
    #           ]
