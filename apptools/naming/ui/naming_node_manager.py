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
""" The node manager for a naming tree. """


# Enthought library imports.
from pyface.tree.api import NodeManager


class NamingNodeManager(NodeManager):
    """ The node manager for a naming tree. """

    ###########################################################################
    # 'NodeManager' interface.
    ###########################################################################

    def get_key(self, node):
        """ Generates a unique key for a node. """

        # fixme: This scheme does NOT allow the same object to be in the tree
        # in more than one place.
        return self._get_hash_value(node.obj)

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _get_hash_value(self, obj):
        """ Returns a hash value for an object. """

        # We do it like this 'cos, for example, using id() on a string
        # doesn't give us what we want, but things like lists aren't
        # hashable, so we can't always use hash()).
        try:
            hash_value = hash(obj)

        except:
            hash_value = id(obj)

        return hash_value

##### EOF #####################################################################
