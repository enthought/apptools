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
""" A tree view of a naming system. """


# Enthought library imports.
from apptools.naming.api import OperationNotSupportedError
from pyface.tree.api import NodeTree
from traits.api import Instance

# Local imports.
from .naming_tree_model import NamingTreeModel


class NamingTree(NodeTree):
    """ A tree view of a naming system. """

    #### 'Tree' interface #####################################################

    # The model that provides the data for the tree.
    model = Instance(NamingTreeModel)

    ###########################################################################
    # 'Tree' interface.
    ###########################################################################

    #### Trait initializers ###################################################

    def _model_default(self):
        """ Initializes the model trait. """

        return NamingTreeModel()

    ###########################################################################
    # 'NamingTree' interface.
    ###########################################################################

    def ensure_visible(self, node):
        """ Make sure that the specified node is visible. """

        try:
            components = node.namespace_name.split('/')

            # Make sure that the tree is expanded down to the context that
            # contains the node.
            binding = self.root
            for atom in components[:-1]:
                binding = binding.obj.lookup_binding(atom)
                self.expand(binding)

            # The context is expanded so we know that the node will be in the
            # node to Id map.
            wxid = self._node_to_id_map.get(self.model.get_key(node), None)
            self.control.EnsureVisible(wxid)

        # We need 'namespace_name' to make this work.  If we don't have it
        # then we simply cannot do this!
        except OperationNotSupportedError:
            binding = None

        return binding

##### EOF #####################################################################
