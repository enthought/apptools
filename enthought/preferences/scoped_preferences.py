""" A preferences node that adds the notion of preferences scopes. """


# Standard library imports.
from os.path import join

# Enthought library imports.
from enthought.etsconfig.api import ETSConfig
from enthought.traits.api import List, Str, Undefined

# Local imports.
from i_preferences import IPreferences
from preferences import Preferences


class ScopedPreferences(Preferences):
    """ A preferences node that adds the notion of preferences scopes.

    Path names passed to the node can either contain scope information or can
    simply be a preference path. In the latter case, the operation takes place
    in the first scope in the node's list of scopes.

    The syntax of a fully qualified path name is::

      scope_name/some/arbitrary/scope/context/path.to.a.preference

    The scope is up to the first '/'. The scope context (if any) is from the
    first '/' to the last '/', and the actual preference path is everything
    after the last '/'.

    e.g. A preference path might look like this::
    
    'project/My Project/my.plugin.id/acme.ui.bgcolor'
    
    The scope is           'project'.
    The scope context is   'My Project/my.plugin.id'
    The preference path is 'acme.ui.bgcolor' 

    There is one drawback to this scheme. If you want to access a scope node
    itself via the 'clear', 'keys', 'node', 'node_exists' or 'node_names'
    methods then you have to append a trailing '/' to the path. Without that,
    the node would try to perform the operation in the first scope.

    e.g. To get the names of the children of the 'application' scope, use::

      scoped.node_names('application/')

    If you did this::

      scoped.node_names('application')

    Then the node would get the first scope and try to find its child node
    called 'application'.

    Of course you can just get the scope via::

      scoped.get_scope('application')

    and then call whatever methods you like on it!
      
    """

    #### 'ScopedPreferences' interface ########################################

    # The scopes (in the order that they should be searched when looking for
    # preferences).
    scopes = List(IPreferences)
    
    ###########################################################################
    # 'IPreferences' interface.
    ###########################################################################
    
    #### Methods where 'path' refers to a preference ####

    def get(self, path, default=None, inherit=False):
        """ Get the value of the preference at the specified path. """

        if len(path) == 0:
            raise ValueError('empty path')

        # If the path contains a specific scope then lookup the preference in
        # just that scope.
        if self._path_contains_scope(path):
            scope_name, path = self._parse_path(path)
            nodes = [self._get_scope(scope_name)]
            
        # Otherwise, try each scope in turn.
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
            raise ValueError('empty path')

        # If the path contains a specific scope then remove the preference from
        # just that scope.
        if self._path_contains_scope(path):
            scope_name, path = self._parse_path(path)
            node = self._get_scope(scope_name)

        # Otherwise, remove the preference from the first scope.
        else:
            node = self.scopes[0]

        node.remove(path)

        return
        
    def set(self, path, value):
        """ Set the value of the preference at the specified path. """

        if len(path) == 0:
            raise ValueError('empty path')

        # If the path contains a specific scope then set the value in that
        # scope.
        if self._path_contains_scope(path):
            scope_name, path = self._parse_path(path)
            node = self._get_scope(scope_name)

        # Otherwise, set the value in the first scope.
        else:
            node = self.scopes[0]

        node.set(path, value)

        return

    #### Methods where 'path' refers to a node ####

    def clear(self, path=''):
        """ Remove all preference from the node at the specified path. """

        # If the path contains a specific scope then remove the preferences
        # from a node in that scope.
        if self._path_contains_scope(path):
            scope_name, path = self._parse_path(path)
            node = self._get_scope(scope_name)

        # Otherwise, remove the preferences from a node in the first scope.
        else:
            node = self.scopes[0]

        return node.clear(path)

    def keys(self, path=''):
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

    def node(self, path=''):
        """ Return the node at the specified path. """

        if len(path) == 0:
            node = self

        else:
            # If the path contains a specific scope then we get the node that
            # scope.
            if self._path_contains_scope(path):
                scope_name, path = self._parse_path(path)
                node = self._get_scope(scope_name)

            # Otherwise, get the node from the first scope.
            else:
                node = self.scopes[0]

            node = node.node(path)

        return node

    def node_exists(self, path=''):
        """ Return True if the node at the specified path exists. """

        # If the path contains a specific scope then look for the node in that
        # scope.
        if self._path_contains_scope(path):
            scope_name, path = self._parse_path(path)
            node = self._get_scope(scope_name)

        # Otherwise, look for the node in the first scope.
        else:
            node = self.scopes[0]

        return node.node_exists(path)

    def node_names(self, path=''):
        """ Return the names of the children of the node at the specified path.

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
    # 'Preferences' interface.
    ###########################################################################

    #### Listener methods ####

    def add_preferences_listener(self, listener, path=''):
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

        return

    def remove_preferences_listener(self, listener, path=''):
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

        return

    #### Persistence methods ####

    def load(self, file_or_filename=None):
        """ Load preferences from a file.

        This loads the preferences into the first scope.

        """

        if file_or_filename is None and len(self.filename) > 0:
            file_or_filename = self.filename
            
        node = self.scopes[0]
        node.load(file_or_filename)

        return

    def save(self, file_or_filename=None):
        """ Save the node's preferences to a file.

        This asks each scope in turn to save its preferences.

        If a file or filename is specified then it is only passed to the first
        scope.

        """

        if file_or_filename is None and len(self.filename) > 0:
            file_or_filename = self.filename

        self.scopes[0].save(file_or_filename)
        for scope in self.scopes[1:]:
            scope.save()

        return

    ###########################################################################
    # 'ScopedPreferences' interface.
    ###########################################################################
    
    def _scopes_default(self):
        """ Trait initializer. """
        
        # The application scope is a persistent scope.
        application_scope = Preferences(
            name     = 'application',
            filename = join(ETSConfig.get_application_home(create=False), 
                            'preferences.ini')
        )

        # The default scope is a transient scope.
        default_scope = Preferences(name='default')

        return [application_scope, default_scope]

    def get_scope(self, scope_name):
        """ Return the scope with the specified name.

        Return None if no such scope exists.

        """

        for scope in self.scopes:
            if scope_name == scope.name:
                break

        else:
            scope = None

        return scope
        
    ###########################################################################
    # Private interface.
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
        """ Return the scope with the specified name.

        Raise a 'ValueError' is no such scope exists.

        """

        scope = self.get_scope(scope_name)
        if scope is None:
            raise ValueError('no such scope %s' % scope_name)

        return scope

    def _path_contains_scope(self, path):
        """ Return True if the path contains a scope component. """

        return '/' in path
    
    def _parse_path(self, path):
        """ 'Parse' the path into two parts, the scope name and the rest! """

        components = path.split('/')

        return components[0], '/'.join(components[1:])

    ###########################################################################
    # Debugging interface.
    ###########################################################################

    def dump(self, indent=''):
        """ Dump the preferences hierarchy to stdout. """

        if indent == '':
            print
            
        print indent, 'Node(%s)' % self.name, self._preferences
        indent += '  '

        for child in self.scopes:
            child.dump(indent)
        
        return
    
#### EOF ######################################################################
