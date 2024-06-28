# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" The interface for a node in a preferences hierarchy. """


# Enthought library imports.
from traits.api import Instance, Interface, Str


class IPreferences(Interface):
    """ The interface for a node in a preferences hierarchy. """

    # The absolute path to this node from the root node (the empty string if
    # this node *is* the root node).
    path = Str

    # The parent node (None if this node *is* the root node).
    parent = Instance("IPreferences")

    # The name of the node relative to its parent (the empty string if this
    # node *is* the root node).
    name = Str

    #### Methods where 'path' refers to a preference ####

    def get(self, path, default=None, inherit=False):
        """Get the value of the preference at the specified path.

        If no value exists for the path (or any part of the path does not
        exist) then return the default value.

        Preference values are *always* returned as strings.

        e.g::

          preferences.set('acme.ui.bgcolor', 'blue')
          preferences.get('acme.ui.bgcolor') -> 'blue'

          preferences.set('acme.ui.width', 100)
          preferences.get('acme.ui.width') -> '100'

          preferences.set('acme.ui.visible', True)
          preferences.get('acme.ui.visible') -> 'True'

        If 'inherit' is True then we allow 'inherited' preference values.

        e.g. If we are looking up::

          'acme.ui.widget.bgcolor'

        and it does not exist then we will also try::

          'acme.ui.bgcolor'
          'acme.bgcolor'
          'bgcolor'

        Raise a 'ValueError' exception if the path is the empty string.

        """

    def remove(self, path):
        """Remove the preference at the specified path.

        Does nothing if no value exists for the path (or any part of the path
        does not exist.

        Raise a 'ValueError' exception if the path is the empty string.

        e.g.::

          preferences.remove('acme.ui.bgcolor')

        """

    def set(self, path, value):
        """Set the value of the preference at the specified path.

        Any missing nodes are created automatically.

        Primitive Python types can be set, but preferences are *always*
        stored and returned as strings.

        e.g::

          preferences.set('acme.ui.bgcolor', 'blue')
          preferences.get('acme.ui.bgcolor') -> 'blue'

          preferences.set('acme.ui.width', 100)
          preferences.get('acme.ui.width') -> '100'

          preferences.set('acme.ui.visible', True)
          preferences.get('acme.ui.visible') -> 'True'

        Raise a 'ValueError' exception if the path is the empty string.

        """

    #### Methods where 'path' refers to a node ####

    def clear(self, path=""):
        """Remove all preference from the node at the specified path.

        If the path is the empty string (the default) then remove the
        preferences in *this* node.

        This does not affect any of the node's children.

        e.g. To clear the preferences out of a node directly::

          preferences.clear()

        Or to clear the preferences of a node at a given path::

          preferences.clear('acme.ui')

        """

    def keys(self, path=""):
        """Return the preference keys of the node at the specified path.

        If the path is the empty string (the default) then return the
        preference keys of *this* node.

        e.g::

          keys = preferences.keys('acme.ui')

        """

    def node(self, path=""):
        """Return the node at the specified path.

        If the path is the empty string (the default) then return *this* node.

        Any missing nodes are created automatically.

        e.g::

          node = preferences.node('acme.ui')
          bgcolor = node.get('bgcolor')

        """

    def node_exists(self, path=""):
        """Return True if the node at the specified path exists

        If the path is the empty string (the default) then return True.

        e.g::

          exists = preferences.exists('acme.ui')

        """

    def node_names(self, path=""):
        """Return the names of the children of the node at the specified path.

        If the path is the empty string (the default) then return the names of
        the children of *this* node.

        e.g::

          names = preferences.node_names('acme.ui')

        """

    #### Persistence methods ####

    def flush(self):
        """Force any changes in the node to the backing store.

        This includes any changes to the node's descendants.

        """
