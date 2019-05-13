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
""" The model for a tree view of a naming system. """


# Enthought library imports.
from apptools.naming.api import Binding
from pyface.tree.api import NodeTreeModel
from traits.api import Instance

# Local imports.
from .context_node_type import ContextNodeType
from .naming_node_manager import NamingNodeManager
from .object_node_type import ObjectNodeType


class NamingTreeModel(NodeTreeModel):
    """ The model for a tree view of a naming system. """

    #### 'TreeModel' interface ################################################

    # The root of the model.
    root = Instance(Binding)

    #### 'NodeTreeModel' interface ############################################

    # The node manager looks after all node types.
    node_manager = Instance(NamingNodeManager)

    ###########################################################################
    # 'NodeTreeModel' interface.
    ###########################################################################

    #### Trait initializers ###################################################

    def _node_manager_default(self):
        """ Initializes the node manaber trait. """

        node_manager = NamingNodeManager()
        node_manager.add_node_type(ContextNodeType())
        node_manager.add_node_type(ObjectNodeType())

        return node_manager

##### EOF #####################################################################
