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
""" The node type for contexts in a naming system. """

from __future__ import print_function

# Enthought library imports.
from apptools.naming.api import Context
from pyface.tree.api import NodeType

# Local imports.
from .context_monitor import ContextMonitor


class ContextNodeType(NodeType):
    """ The node type for contexts in a naming system. """

    ###########################################################################
    # 'NodeType' interface.
    ###########################################################################

    # 'node' in this case is a 'Binding' instance whose 'obj' trait is a
    # 'Context' instance.
    def is_type_for(self, node):
        """ Returns True if this node type recognizes a node. """

        return isinstance(node.obj, Context)

    def allows_children(self, node):
        """ Does the node allow children (ie. a folder vs a file). """

        return True

    def has_children(self, node):
        """ Returns True if a node has children, otherwise False. """

        return len(node.obj.list_names('')) > 0

    def get_children(self, node):
        """ Returns the children of a node. """

        return node.obj.list_bindings('')

    def get_drag_value(self, node):
        """ Get the value that is dragged for a node. """

        return node.obj

    def is_editable(self, node):
        """ Returns True if the node is editable, otherwise False. """

        # You can't rename the root context!
        return node.context is not None

    def get_text(self, node):
        """ Returns the label text for a node. """

        return node.name

    def can_set_text(self, node, text):
        """ Returns True if the node's label can be set. """

        # The parent context will NOT be None here (see 'is_editable').
        parent = node.context

        return len(text.strip()) > 0 and text not in parent.list_names('')

    def set_text(self, node, text):
        """ Sets the label text for a node. """

        print('Setting text on', node.name, node.obj)
        print('Context details', node.obj.name, node.obj.path)

        # Do the rename in the naming system.
        node.context.rename(node.name, text)

        # Update the binding.
        node.name = text

        return

    def get_monitor(self, node):
        """ Returns a monitor that detects changes to a node. """

        return ContextMonitor(node=node)

##### EOF #####################################################################
