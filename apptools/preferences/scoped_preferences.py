# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" A preferences node that adds the notion of preferences scopes. """

# Standard library imports.
from os.path import join

# Enthought library imports.
from traits.etsconfig.api import ETSConfig
from traits.api import List, Str, Undefined

# Local imports.
from .i_preferences import IPreferences
from .preferences import Preferences


class ScopedPreferences(Preferences):
    """A preferences node that adds the notion of preferences scopes.

    Scopes provide a way to access preferences in a precedence order, usually
    depending on where they came from, for example from the command-line,
    or set by the user in a preferences file, or the defaults (set by the
    developer).

    By default, this class provides two scopes - 'application' which is
    persistent and 'default' which is not.

    Path names passed to 'ScopedPreferences' nodes can be either::

        a) a preference path as used in a standard 'Preferences' node, e.g::

        'acme.widget.bgcolor'.

        In this case the operation either takes place in the primary scope
        (for operations such as 'set' etc), or on all scopes in precedence
        order (for operations such as 'get' etc).

        or

        b) a preference path that refers to a specific scope e.g::

        'default/acme.widget.bgcolor'

        In this case the operation takes place *only* in the specified scope.

    There is one drawback to this scheme. If you want to access a scope node
    itself via the 'clear', 'keys', 'node', 'node_exists' or 'node_names'
    methods then you have to append a trailing '/' to the path. Without that,
    the node would try to perform the operation in the primary scope.

    e.g. To get the names of the children of the 'application' scope, use::

        scoped.node_names('application/')

    If you did this::

        scoped.node_names('application')

    Then the node would get the primary scope and try to find its child node
    called 'application'.

    Of course you can just get the scope via::

        application_scope = scoped.get_scope('application')

    and then call whatever methods you like on it - which is definitely more
    intentional and is highly recommended::

        application_scope.node_names()

    """

    #### 'ScopedPreferences' interface ########################################

    # The file that the application scope preferences are stored in.
    #
    # Defaults to:-
    #
    #    os.path.join(ETSConfig.application_home, 'preferences.ini')
    application_preferences_filename = Str

    # The scopes (in the order that they should be searched when looking up
    # preferences).
    #
    # By default, this class provides two scopes - 'application' which is
    # persistent and 'default' which is not.
    scopes = List(IPreferences)

    # The name of the 'primary' scope.
    #
    # This is the scope that operations take place in if no scope is specified
    # in a given path (for the 'get' operation, if no scope is specified the
    # operation takes place in *all* scopes in order of precedence). If this is
    # the empty string (the default) then the primary scope is the first scope
    # in the 'scopes' list.
    primary_scope_name = Str

    ###########################################################################
    # 'IPreferences' protocol.
    ###########################################################################

    #### Methods where 'path' refers to a preference ####

    def get(self, path, default=None, inherit=False):
        """ Get the value of the preference at the specified path. """

        if len(path) == 0:
            raise ValueError("empty path")

        # If the path contains a specific scope then lookup the preference in
        # just that scope.
        if self._path_contains_scope(path):
            scope_name, path = self._parse_path(path)
            nodes = [self._get_scope(scope_name)]

        # Otherwise, try each scope in turn (i.e. in order of precedence).
        else:
            nodes = self.scopes

        # Try all nodes first (without inheritance even if specified).
        value = self._get(path, Undefined, nodes, inherit=False)
        if value is Undefined:
            if inherit:
                value = self._get(path, default, nodes, inherit=True)

            else:
                value = default

        return value

    def remove(self, path):
        """ Remove the preference at the specified path. """

        if len(path) == 0:
            raise ValueError("empty path")

        # If the path contains a specific scope then remove the preference from
        # just that scope.
        if self._path_contains_scope(path):
            scope_name, path = self._parse_path(path)
            node = self._get_scope(scope_name)

        # Otherwise, remove the preference from the primary scope.
        else:
            node = self._get_primary_scope()

        node.remove(path)

    def set(self, path, value):
        """ Set the value of the preference at the specified path. """

        if len(path) == 0:
            raise ValueError("empty path")

        # If the path contains a specific scope then set the value in that
        # scope.
        if self._path_contains_scope(path):
            scope_name, path = self._parse_path(path)
            node = self._get_scope(scope_name)

        # Otherwise, set the value in the primary scope.
        else:
            node = self._get_primary_scope()

        node.set(path, value)

    #### Methods where 'path' refers to a node ####

    def clear(self, path=""):
        """ Remove all preference from the node at the specified path. """

        # If the path contains a specific scope then remove the preferences
        # from a node in that scope.
        if self._path_contains_scope(path):
            scope_name, path = self._parse_path(path)
            node = self._get_scope(scope_name)

        # Otherwise, remove the preferences from a node in the primary scope.
        else:
            node = self._get_primary_scope()

        return node.clear(path)

    def keys(self, path=""):
        """ Return the preference keys of the node at the specified path. """

        # If the path contains a specific scope then get the keys of the node
        # in that scope.
        if self._path_contains_scope(path):
            scope_name, path = self._parse_path(path)
            nodes = [self._get_scope(scope_name)]

        # Otherwise, merge the keys of the node in all scopes.
        else:
            nodes = self.scopes

        keys = set()
        for node in nodes:
            keys.update(node.node(path).keys())

        return list(keys)

    def node(self, path=""):
        """ Return the node at the specified path. """

        if len(path) == 0:
            node = self

        else:
            # If the path contains a specific scope then we get the node that
            # scope.
            if self._path_contains_scope(path):
                scope_name, path = self._parse_path(path)
                node = self._get_scope(scope_name)

            # Otherwise, get the node from the primary scope.
            else:
                node = self._get_primary_scope()

            node = node.node(path)

        return node

    def node_exists(self, path=""):
        """ Return True if the node at the specified path exists. """

        # If the path contains a specific scope then look for the node in that
        # scope.
        if self._path_contains_scope(path):
            scope_name, path = self._parse_path(path)
            node = self._get_scope(scope_name)

        # Otherwise, look for the node in the primary scope.
        else:
            node = self._get_primary_scope()

        return node.node_exists(path)

    def node_names(self, path=""):
        """Return the names of the children of the node at the specified path.
        """

        # If the path contains a specific scope then get the names of the
        # children of the node in that scope.
        if self._path_contains_scope(path):
            scope_name, path = self._parse_path(path)
            nodes = [self._get_scope(scope_name)]

        # Otherwise, merge the names of the children of the node in all scopes.
        else:
            nodes = self.scopes

        names = set()
        for node in nodes:
            names.update(node.node(path).node_names())

        return list(names)

    ###########################################################################
    # 'Preferences' protocol.
    ###########################################################################

    #### Listener methods ####

    def add_preferences_listener(self, listener, path=""):
        """ Add a listener for changes to a node's preferences. """

        # If the path contains a specific scope then add a preferences listener
        # to the node in that scope.
        if self._path_contains_scope(path):
            scope_name, path = self._parse_path(path)
            nodes = [self._get_scope(scope_name)]

        # Otherwise, add a preferences listener to the node in all scopes.
        else:
            nodes = self.scopes

        for node in nodes:
            node.add_preferences_listener(listener, path)

    def remove_preferences_listener(self, listener, path=""):
        """ Remove a listener for changes to a node's preferences. """

        # If the path contains a specific scope then remove a preferences
        # listener from the node in that scope.
        if self._path_contains_scope(path):
            scope_name, path = self._parse_path(path)
            nodes = [self._get_scope(scope_name)]

        # Otherwise, remove a preferences listener from the node in all scopes.
        else:
            nodes = self.scopes

        for node in nodes:
            node.remove_preferences_listener(listener, path)

    #### Persistence methods ####

    def load(self, file_or_filename=None):
        """Load preferences from a file.

        This loads the preferences into the primary scope.

        fixme: I'm not sure it is worth providing an implentation here. I
        think it would be better to encourage people to explicitly reference
        a particular scope.

        """

        if file_or_filename is None and len(self.filename) > 0:
            file_or_filename = self.filename

        node = self._get_primary_scope()
        node.load(file_or_filename)

    def save(self, file_or_filename=None):
        """Save the node's preferences to a file.

        This asks each scope in turn to save its preferences.

        If a file or filename is specified then it is only passed to the
        primary scope.

        """

        if file_or_filename is None and len(self.filename) > 0:
            file_or_filename = self.filename

        self._get_primary_scope().save(file_or_filename)
        for scope in self.scopes:
            if scope is not self._get_primary_scope():
                scope.save()

    ###########################################################################
    # 'ScopedPreferences' protocol.
    ###########################################################################

    def _application_preferences_filename_default(self):
        """ Trait initializer. """

        return join(ETSConfig.application_home, "preferences.ini")

    # fixme: In hindsight, I don't think this class should have provided
    # default scopes. This should have been an 'abstract' class that could
    # be subclassed by classes providing specific scopes.
    def _scopes_default(self):
        """ Trait initializer. """

        scopes = [
            Preferences(
                name="application",
                filename=self.application_preferences_filename,
            ),
            Preferences(name="default"),
        ]

        return scopes

    def get_scope(self, scope_name):
        """Return the scope with the specified name.

        Return None if no such scope exists.

        """

        for scope in self.scopes:
            if scope_name == scope.name:
                break

        else:
            scope = None

        return scope

    ###########################################################################
    # Private protocol.
    ###########################################################################

    def _get(self, path, default, nodes, inherit):
        """ Get a preference from a list of nodes. """

        for node in nodes:
            value = node.get(path, Undefined, inherit)
            if value is not Undefined:
                break

        else:
            value = default

        return value

    def _get_scope(self, scope_name):
        """Return the scope with the specified name.

        Raise a 'ValueError' is no such scope exists.

        """

        scope = self.get_scope(scope_name)
        if scope is None:
            raise ValueError("no such scope %s" % scope_name)

        return scope

    def _get_primary_scope(self):
        """Return the primary scope.

        By default, this is the first scope.

        """

        if len(self.primary_scope_name) > 0:
            scope = self._get_scope(self.primary_scope_name)

        else:
            scope = self.scopes[0]

        return scope

    def _path_contains_scope(self, path):
        """ Return True if the path contains a scope component. """

        return "/" in path

    def _parse_path(self, path):
        """ 'Parse' the path into two parts, the scope name and the rest! """

        components = path.split("/")

        return components[0], "/".join(components[1:])

    ###########################################################################
    # Debugging interface.
    ###########################################################################

    def dump(self, indent=""):
        """ Dump the preferences hierarchy to stdout. """

        if indent == "":
            print()

        print(indent, "Node(%s)" % self.name, self._preferences)
        indent += "  "

        for child in self.scopes:
            child.dump(indent)
