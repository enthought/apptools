# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" The default implementation of a node in a preferences hierarchy. """

# Standard library imports.
import logging
import threading

# Enthought library imports.
from traits.api import Any, Callable, Dict, HasTraits, Instance, List
from traits.api import Property, Str, Undefined, provides

# Local imports.
from .i_preferences import IPreferences


# Logging.
logger = logging.getLogger(__name__)


@provides(IPreferences)
class Preferences(HasTraits):
    """ The default implementation of a node in a preferences hierarchy. """

    #### 'IPreferences' interface #############################################

    # The absolute path to this node from the root node (the empty string if
    # this node *is* the root node).
    path = Property(Str)

    # The parent node (None if this node *is* the root node).
    parent = Instance(IPreferences)

    # The name of the node relative to its parent (the empty string if this
    # node *is* the root node).
    name = Str

    #### 'Preferences' interface ##############################################

    # The default name of the file used to persist the preferences (if no
    # filename is passed in to the 'load' and 'save' methods, then this is
    # used instead).
    filename = Str

    #### Protected 'Preferences' interface ####################################

    # A lock to make access to the node thread-safe.
    #
    # fixme: There *should* be no need to declare this as a trait, but if we
    # don't then we have problems using nodes in the preferences manager UI.
    # It is something to do with 'cloning' the node for use in a 'modal' traits
    # UI... Hmmm...
    _lk = Any

    # The node's children.
    _children = Dict(Str, IPreferences)

    # The node's preferences.
    _preferences = Dict(Str, Any)

    # Listeners for changes to the node's preferences.
    #
    # The callable must take 4 arguments, e.g::
    #
    # listener(node, key, old, new)
    _preferences_listeners = List(Callable)

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **traits):
        """ Constructor. """

        # A lock to make access to the '_children', '_preferences' and
        # '_preferences_listeners' traits thread-safe.
        self._lk = threading.Lock()

        # Base class constructor.
        super().__init__(**traits)

        # If a filename has been specified then load the preferences from it.
        if len(self.filename) > 0:
            self.load()

    ###########################################################################
    # 'IPreferences' interface.
    ###########################################################################

    #### Trait properties #####################################################

    def _get_path(self):
        """ Property getter. """

        names = []

        node = self
        while node.parent is not None:
            names.append(node.name)
            node = node.parent

        names.reverse()

        return ".".join(names)

    #### Methods ##############################################################

    #### Methods where 'path' refers to a preference ####

    def get(self, path, default=None, inherit=False):
        """ Get the value of the preference at the specified path. """

        if len(path) == 0:
            raise ValueError("empty path")

        components = path.split(".")

        # If there is only one component in the path then the operation takes
        # place in this node.
        if len(components) == 1:
            value = self._get(path, Undefined)

        # Otherwise, find the next node and pass the rest of the path to that.
        else:
            node = self._get_child(components[0])
            if node is not None:
                value = node.get(".".join(components[1:]), Undefined)

            else:
                value = Undefined

        # If inherited values are allowed then try those as well.
        #
        # e.g. 'acme.ui.widget.bgcolor'
        #      'acme.ui.bgcolor'
        #      'acme.bgcolor'
        #      'bgcolor'
        while inherit and value is Undefined and len(components) > 1:
            # Remove the penultimate component...
            #
            # e.g. 'acme.ui.widget.bgcolor' -> 'acme.ui.bgcolor'
            del components[-2]

            # ... and try that.
            value = self.get(".".join(components), default=Undefined)

        if value is Undefined:
            value = default

        return value

    def remove(self, path):
        """ Remove the preference at the specified path. """

        if len(path) == 0:
            raise ValueError("empty path")

        components = path.split(".")

        # If there is only one component in the path then the operation takes
        # place in this node.
        if len(components) == 1:
            self._remove(path)

        # Otherwise, find the next node and pass the rest of the path to that.
        else:
            node = self._get_child(components[0])
            if node is not None:
                node.remove(".".join(components[1:]))

    def set(self, path, value):
        """ Set the value of the preference at the specified path. """

        if len(path) == 0:
            raise ValueError("empty path")

        components = path.split(".")

        # If there is only one component in the path then the operation takes
        # place in this node.
        if len(components) == 1:
            self._set(path, value)

        # Otherwise, find the next node (creating it if it doesn't exist)
        # and pass the rest of the path to that.
        else:
            node = self._node(components[0])
            node.set(".".join(components[1:]), value)

    #### Methods where 'path' refers to a node ####

    def clear(self, path=""):
        """ Remove all preferences from the node at the specified path. """

        # If the path is empty then the operation takes place in this node.
        if len(path) == 0:
            self._clear()

        # Otherwise, find the next node and pass the rest of the path to that.
        else:
            components = path.split(".")

            node = self._get_child(components[0])
            if node is not None:
                node.clear(".".join(components[1:]))

    def keys(self, path=""):
        """ Return the preference keys of the node at the specified path. """

        # If the path is empty then the operation takes place in this node.
        if len(path) == 0:
            keys = self._keys()

        # Otherwise, find the next node and pass the rest of the path to that.
        else:
            components = path.split(".")

            node = self._get_child(components[0])
            if node is not None:
                keys = node.keys(".".join(components[1:]))

            else:
                keys = []

        return keys

    def node(self, path=""):
        """ Return the node at the specified path. """

        # If the path is empty then the operation takes place in this node.
        if len(path) == 0:
            node = self

        # Otherwise, find the next node and pass the rest of the path to that.
        else:
            components = path.split(".")

            node = self._node(components[0])
            node = node.node(".".join(components[1:]))

        return node

    def node_exists(self, path=""):
        """ Return True if the node at the specified path exists. """

        # If the path is empty then the operation takes place in this node.
        if len(path) == 0:
            exists = True

        # Otherwise, find the next node and pass the rest of the path to that.
        else:
            components = path.split(".")

            node = self._get_child(components[0])
            if node is not None:
                exists = node.node_exists(".".join(components[1:]))

            else:
                exists = False

        return exists

    def node_names(self, path=""):
        """Return the names of the children of the node at the specified path.
        """

        # If the path is empty then the operation takes place in this node.
        if len(path) == 0:
            names = self._node_names()

        # Otherwise, find the next node and pass the rest of the path to that.
        else:
            components = path.split(".")

            node = self._get_child(components[0])
            if node is not None:
                names = node.node_names(".".join(components[1:]))

            else:
                names = []

        return names

    #### Persistence methods ####

    def flush(self):
        """Force any changes in the node to the backing store.

        This includes any changes to the node's descendants.

        """

        self.save()

    ###########################################################################
    # 'Preferences' interface.
    ###########################################################################

    #### Listener methods ####

    def add_preferences_listener(self, listener, path=""):
        """ Add a listener for changes to a node's preferences. """

        # If the path is empty then the operation takes place in this node.
        if len(path) == 0:
            self._add_preferences_listener(listener)

        # Otherwise, find the next node and pass the rest of the path to that.
        else:
            components = path.split(".")

            node = self._node(components[0])
            node.add_preferences_listener(listener, ".".join(components[1:]))

    def remove_preferences_listener(self, listener, path=""):
        """ Remove a listener for changes to a node's preferences. """

        # If the path is empty then the operation takes place in this node.
        if len(path) == 0:
            self._remove_preferences_listener(listener)

        # Otherwise, find the next node and pass the rest of the path to that.
        else:
            components = path.split(".")

            node = self._node(components[0])
            node.remove_preferences_listener(
                listener, ".".join(components[1:])
            )

    #### Persistence methods ####

    def load(self, file_or_filename=None):
        """Load preferences from a file.

        This is a *merge* operation i.e. the contents of the file are added to
        the node.

        This implementation uses 'ConfigObj' files.

        """

        if file_or_filename is None:
            file_or_filename = self.filename

        logger.debug("loading preferences from <%s>", file_or_filename)

        # Do the import here so that we don't make 'ConfigObj' a requirement
        # if preferences aren't ever persisted (or a derived class chooses to
        # use a different persistence mechanism).
        from configobj import ConfigObj

        config_obj = ConfigObj(file_or_filename, encoding="utf-8")

        # 'name' is the section name, 'value' is a dictionary containing the
        # name/value pairs in the section (the actual preferences ;^).
        for name, value in config_obj.items():
            # Create/get the node from the section name.
            components = name.split(".")

            node = self
            for component in components:
                node = node._node(component)

            # Add the contents of the section to the node.
            self._add_dictionary_to_node(node, value)

    def save(self, file_or_filename=None):
        """Save the node's preferences to a file.

        This implementation uses 'ConfigObj' files.

        """

        if file_or_filename is None:
            file_or_filename = self.filename

        # If no file or filename is specified then don't save the preferences!
        if len(file_or_filename) > 0:
            # Do the import here so that we don't make 'ConfigObj' a
            # requirement if preferences aren't ever persisted (or a derived
            # class chooses to use a different persistence mechanism).
            from configobj import ConfigObj

            logger.debug("saving preferences to <%s>", file_or_filename)

            config_obj = ConfigObj(file_or_filename, encoding="utf-8")
            self._add_node_to_dictionary(self, config_obj)
            config_obj.write()

    ###########################################################################
    # Protected 'Preferences' interface.
    #
    # These are the only methods that should access the protected '_children'
    # and '_preferences' traits. This helps make it easy to subclass this class
    # to create other implementations (all the subclass has to do is to
    # implement these protected methods).
    #
    ###########################################################################

    def _add_dictionary_to_node(self, node, dictionary):
        """ Add the contents of a dictionary to a node's preferences. """

        with self._lk:
            node._preferences.update(dictionary)

    def _add_node_to_dictionary(self, node, dictionary):
        """ Add a node's preferences to a dictionary. """

        # This method never manipulates the '_preferences' trait directly.
        # Instead it does eveything via the other protected methods and hence
        # doesn't need to grab the lock.
        if len(node._keys()) > 0:
            dictionary[node.path] = {}
            for key in node._keys():
                dictionary[node.path][key] = node._get(key)

        for name in node._node_names():
            self._add_node_to_dictionary(node._get_child(name), dictionary)

    def _add_preferences_listener(self, listener):
        """ Add a listener for changes to thisnode's preferences. """

        with self._lk:
            self._preferences_listeners.append(listener)

    def _clear(self):
        """ Remove all preferences from this node. """

        with self._lk:
            self._preferences.clear()

    def _create_child(self, name):
        """ Create a child of this node with the specified name. """

        with self._lk:
            child = self._children[name] = Preferences(name=name, parent=self)

        return child

    def _get(self, key, default=None):
        """ Get the value of a preference in this node. """

        with self._lk:
            value = self._preferences.get(key, default)

        return value

    def _get_child(self, name):
        """Return the child of this node with the specified name.

        Return None if no such child exists.

        """

        with self._lk:
            child = self._children.get(name)

        return child

    def _keys(self):
        """ Return the preference keys of this node. """

        with self._lk:
            keys = list(self._preferences.keys())

        return keys

    def _node(self, name):
        """Return the child of this node with the specified name.

        Create the child node if it does not exist.

        """

        node = self._get_child(name)
        if node is None:
            node = self._create_child(name)

        return node

    def _node_names(self):
        """ Return the names of the children of this node. """

        with self._lk:
            node_names = list(self._children.keys())

        return node_names

    def _remove(self, name):
        """ Remove a preference value from this node. """

        with self._lk:
            if name in self._preferences:
                del self._preferences[name]

    def _remove_preferences_listener(self, listener):
        """ Remove a listener for changes to the node's preferences. """

        with self._lk:
            if listener in self._preferences_listeners:
                self._preferences_listeners.remove(listener)

    def _set(self, key, value):
        """ Set the value of a preference in this node. """

        # everything must be unicode encoded so that ConfigObj configuration
        # can properly serialize the data. Python str are supposed to be ASCII
        # encoded.
        value = str(value)

        with self._lk:
            old = self._preferences.get(key)
            self._preferences[key] = value

            # If the value is unchanged then don't call the listeners!
            if old == value:
                listeners = []

            else:
                listeners = self._preferences_listeners[:]

        for listener in listeners:
            listener(self, key, old, value)

    ###########################################################################
    # Debugging interface.
    ###########################################################################

    def dump(self, indent=""):
        """ Dump the preferences hierarchy to stdout. """

        if indent == "":
            print()

        print(indent, "Node(%s)" % self.name, self._preferences)
        indent += "  "

        for child in self._children.values():
            child.dump(indent)
