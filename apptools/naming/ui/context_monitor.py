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
""" A monitor that detects changes to a naming context. """


# Enthought library imports.
from pyface.tree.api import NodeMonitor


class ContextMonitor(NodeMonitor):
    """ A monitor that detects changes to a naming context. """

    ###########################################################################
    # 'NodeMonitor' interface.
    ###########################################################################

    def start(self):
        """ Start listening to changes to the object. """

        context = self.node.obj

        context.on_trait_change(self._on_object_added, 'object_added')
        context.on_trait_change(self._on_object_changed, 'object_changed')
        context.on_trait_change(self._on_object_removed, 'object_removed')
        context.on_trait_change(self._on_object_renamed, 'object_renamed')
        context.on_trait_change(self._on_context_changed, 'context_changed')

        return

    def stop(self):
        """ Stop listening to changes to the object. """

        context = self.node.obj

        context.on_trait_change(
            self._on_object_added, 'object_added', remove=True
        )

        context.on_trait_change(
            self._on_object_changed, 'object_changed', remove=True
        )

        context.on_trait_change(
            self._on_object_removed, 'object_removed', remove=True
        )

        context.on_trait_change(
            self._on_object_renamed, 'object_renamed', remove=True
        )

        context.on_trait_change(
            self._on_context_changed, 'context_changed', remove=True
        )

        return

    ###########################################################################
    # Private interface.
    ###########################################################################

    #### Trait event handlers #################################################

    def _on_object_added(self, event):
        """ Called when an object has been added to the context. """

        self.fire_nodes_inserted([event.new_binding])

        return

    def _on_object_changed(self, event):
        """ Called when an object in the context has been changed. """

        # fixme: Can we get enough information to fire a 'nodes_replaced'
        # event?  Something a little more granular than this!
        self.fire_structure_changed()

        return

    def _on_object_removed(self, event):
        """ Called when an object has been removed from the context. """

        self.fire_nodes_removed([event.old_binding])

        return

    def _on_object_renamed(self, event):
        """ Called when an object has been renamed in the context. """

        self.fire_nodes_replaced([event.old_binding], [event.new_binding])

        return

    def _on_context_changed(self, event):
        """ Called when a context has changed dramatically. """
        self.fire_structure_changed()

        return

##### EOF #####################################################################
