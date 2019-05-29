""" Managers for submenus of the Help menu.

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

# Enthought library imports.
from envisage.api import IExtensionPointUser, IExtensionRegistry
from pyface.action.api import Group, MenuManager
from traits.api import Any, provides, Instance, List, Property

# Local imports.
from .action.doc_action import DocAction
from .action.demo_action import DemoAction
from .action.example_action import ExampleAction
from .action.load_url_action import LoadURLAction
from .examples_preferences import ExamplesPreferences
from .i_help_doc import IHelpDoc
from .i_help_code import IHelpCode

# Logging.
logger = logging.getLogger(__name__)

# This module's package.
PKG = '.'.join(__name__.split('.')[:-1])

@provides(IExtensionPointUser)
class HelpSubmenuManager(MenuManager):
    """ Base class for managers of submenus of the Help menu.

        This class is adapted from
        pyface.ui.workbench.action.view_menu_manager.ViewMenuManager.
    """


    ### IExtensionPointUser interface
    extension_registry = Property(Instance(IExtensionRegistry))

    def _get_extension_registry(self):
        return self.window.application.extension_registry

    #### 'ActionManager' interface ############################################

    # All of the groups in the manager.
    groups = List(Group)

    #### 'Private' interface ##################################################

    # The group containing the actual actions.
    _item_group = Any

    ###########################################################################
    # 'ActionManager' interface.
    ###########################################################################

    def _groups_default(self):
        """ Trait initializer. """

        groups = []

        # Add a group containing items for all contributed documents.
        self._item_group = self._create_item_group(self.window)
        groups.append(self._item_group)

        return groups

    ###########################################################################
    # Private interface.
    ###########################################################################
    def _clear_group(self, group):
        """ Remove all items in a group. """

        group.destroy()
        group.clear()

        return

    def _create_item_group(self, window):
        """ Creates a group containing the items. """

        group = Group()
        self._initialize_item_group(window, group)

        return group

    def _initialize_item_group(self, window, group):
        """ Initializes a group containing the items. """
        raise NotImplementedError

class DocumentsMenuManager(HelpSubmenuManager):
    """ Controls the 'Help/Documents' menu.
    """

    #### 'ActionManager' interface ############################################

    # The manager's unique identifier (if it has one).
    id = 'Documents'

    #### 'MenuManager' interface ##############################################

    # The menu manager's name (if the manager is a sub-menu, this is what its
    # label will be).
    name = u'&Documents'

    #### 'DocMenuManager' interface ##########################################

    # The HelpDocs for which this manager displays menu items.
    help_doc_list = List(IHelpDoc, allow_none=True)

    def _help_doc_list_default(self):
        return self.extension_registry.get_extensions(PKG + '.help_docs')

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _initialize_item_group(self, window, group):
        """ Initializes a group containing the items. """

        docs = self.help_doc_list
        docs.sort(None, lambda doc: doc.label)

        for doc in docs:
            #logger.info('Adding Helpaction for "%s", %s' % (doc.label, str(doc)))
            group.append(
                DocAction(name=doc.label, window=window)
                )

        return

class DemosMenuManager(HelpSubmenuManager):
    """ Controls the 'Help/Demos' menu.
    """

    #### 'ActionManager' interface ############################################

    # The manager's unique identifier (if it has one).
    id = 'Demos'

    #### 'MenuManager' interface ##############################################

    # The menu manager's name (if the manager is a sub-menu, this is what its
    # label will be).
    name = u'D&emos'

    #### 'DemoMenuManager' interface ##########################################

    # The HelpCode for which this manager displays menu items.
    help_demo_list = List(IHelpCode, allow_none=True)

    def _help_demo_list_default(self):
        return self.extension_registry.get_extensions(PKG + '.help_demos')

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _initialize_item_group(self, window, group):
        """ Initializes a group containing the items. """

        demos = self.help_demo_list
        demos.sort(None, lambda demo: demo.label)

        for demo in demos:
            group.append(
                DemoAction(name=demo.label, window=window)
                )

        return

class ExamplesMenuManager(HelpSubmenuManager):
    """ Controls the 'Help/Examples' menu.
    """

    #### 'ActionManager' interface ############################################

    # The manager's unique identifier (if it has one).
    id = 'Examples'

    #### 'MenuManager' interface ##############################################

    # The menu manager's name (if the manager is a sub-menu, this is what its
    # label will be).
    name = u'&Examples'

    #### 'ExampleMenuManager' interface ##########################################

    # The HelpCode for which this manager displays menu items.
    help_example_list = List(IHelpCode, allow_none=True)

    def _help_example_list_default(self):
        return self.extension_registry.get_extensions(PKG + '.help_examples')

    # Preferences for examples
    preferences = Instance(ExamplesPreferences, ())

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _initialize_item_group(self, window, group):
        """ Initializes a group containing the items. """

        examples = self.help_example_list
        examples.sort(None, lambda example: example.label)

        for ex in examples:
            group.append(
                ExampleAction(name=ex.label, window=window,
                                  preferences=self.preferences)
                )

        return


class DownloadsMenuManager(HelpSubmenuManager):
    """ Controls the 'Help/Downloads' or 'Downloads'menu.
    """

    #### 'ActionManager' interface ############################################

    # The manager's unique identifier (if it has one).
    id = 'Downloads'

    #### 'MenuManager' interface ##############################################

    # The menu manager's name (if the manager is a sub-menu, this is what its
    # label will be).
    name = u'&Downloads'

    #### 'DocMenuManager' interface ##########################################

    # The URLs for which this manager displays menu items.
    help_download_list = List(IHelpDoc, allow_none=True)

    def _help_download_list_default(self):
        return self.extension_registry.get_extensions(PKG + '.help_downloads')

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _initialize_item_group(self, window, group):
        """ Initializes a group containing the items. """

        urls = self.help_download_list
        #docs.sort(None, lambda doc: doc.label)

        for url in urls:
            group.append(
                LoadURLAction(name=url.label, window=window)
                )

        return
#### EOF ######################################################################
