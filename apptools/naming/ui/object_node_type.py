#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Enthought, Inc.
# Description: <Enthought naming package component>
#------------------------------------------------------------------------------
""" The node type for NON-contexts in a naming system. """


# Enthought library imports.
from apptools.naming.api import Context
from pyface.tree.api import NodeType


class ObjectNodeType(NodeType):
    """ The node type for NON-contexts in a naming system. """

    ###########################################################################
    # 'NodeType' interface.
    ###########################################################################

    # 'node' in this case is a 'Binding' instance.
    def is_type_for(self, node):
        """ Returns True if this node type recognized a node. """

        return True

    def allows_children(self, node):
        """ Does the node allow children (ie. a folder vs a file). """

        return False

    def get_drag_value(self, node):
        """ Get the value that is dragged for a node. """

        return node.obj

    def is_editable(self, node):
        """ Returns True if the node is editable, otherwise False.

        If the node is editable, its text can be set via the UI.

        """

        return True

    def get_text(self, node):
        """ Returns the label text for a node. """

        return node.name

    def can_set_text(self, node, text):
        """ Returns True if the node's label can be set. """

        # The parent context will NOT be None here (an object is ALWAYS
        # contained in a context).
        parent = node.context

        return len(text.strip()) > 0 and text not in parent.list_names('')

    def set_text(self, node, text):
        """ Sets the label text for a node. """

        node.context.rename(node.name, text)
        node.name = text

        return

##### EOF #####################################################################
