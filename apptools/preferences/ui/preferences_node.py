# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Abstract base class for a node in a preferences dialog. """

# Enthought library imports.
from traits.api import Delegate, Instance

# Local imports.
from .i_preferences_page import IPreferencesPage
from .tree_item import TreeItem


class PreferencesNode(TreeItem):
    """Abstract base class for a node in a preferences dialog.

    A preferences node has a name and an image which are used to represent the
    node in a preferences dialog (usually in the form of a tree).

    """

    #### 'PreferenceNode' interface ###########################################

    # The page's help identifier (optional). If a help Id *is* provided then
    # there will be a 'Help' button shown on the preference page.
    help_id = Delegate("page")

    # The page name (this is what is shown in the preferences dialog.
    name = Delegate("page")

    # The page that we are a node for.
    page = Instance(IPreferencesPage)

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __str__(self):
        """ Returns the string representation of the item. """

        if self.page is None:
            s = "root"

        else:
            s = self.page.name

        return s

    __repr__ = __str__

    ###########################################################################
    # 'PreferencesNode' interface.
    ###########################################################################

    def create_page(self, parent):
        """ Creates the preference page for this node. """

        return self.page.create_control(parent)

    def lookup(self, name):
        """Returns the child of this node with the specified Id.

        Returns None if no such child exists.

        """

        for node in self.children:
            if node.name == name:
                break

        else:
            node = None

        return node

    ###########################################################################
    # Debugging interface.
    ###########################################################################

    def dump(self, indent=""):
        """ Pretty-print the node to stdout. """

        print(indent, "Node", str(self))

        for child in self.children:
            child.dump(indent + "  ")
