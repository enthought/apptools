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
""" A Python File System context. """


# Standard library imports.
import glob
import logging
import os
from os.path import join, splitext

# Third-party library imports.
import six.moves.cPickle as pickle

# Enthought library imports.
from apptools.io.api import File
from traits.api import Any, Dict, Instance, Property, Str

# Local imports.
from .address import Address
from .binding import Binding
from .context import Context
from .dir_context import DirContext
from .exception import NameNotFoundError, NotContextError
from .naming_event import NamingEvent
from .naming_manager import naming_manager
from .object_serializer import ObjectSerializer
from .pyfs_context_factory import PyFSContextFactory
from .pyfs_object_factory import PyFSObjectFactory
from .pyfs_state_factory import PyFSStateFactory
from .reference import Reference
from .referenceable import Referenceable


# Setup a logger for this module.
logger = logging.getLogger(__name__)


# The name of the 'special' file in which we store object attributes.
ATTRIBUTES_FILE = '__attributes__'

# Constants for environment property keys.
FILTERS = "apptools.naming.pyfs.filters"
OBJECT_SERIALIZERS = "apptools.naming.pyfs.object.serializers"


# The default environment.
ENVIRONMENT = {
    #### 'Context' properties #################################################

    # Object factories.
    Context.OBJECT_FACTORIES : [PyFSObjectFactory(), PyFSContextFactory()],

    # State factories.
    Context.STATE_FACTORIES  : [PyFSStateFactory()],

    #### 'PyFSContext' properties #############################################

    # Object serializers.
    OBJECT_SERIALIZERS : [ObjectSerializer()],

    # List of filename patterns to ignore.  These patterns are passed to
    # 'glob.glob', so things like '*.pyc' will do what you expect.
    #
    # fixme: We should have a generalized filter mechanism here, and '.svn'
    # should be moved elsewhere!
    FILTERS : [ATTRIBUTES_FILE, '.svn']
}


class PyFSContext(DirContext, Referenceable):
    """ A Python File System context.

    This context represents a directory on a local file system.

    """

    # The name of the 'special' file in which we store object attributes.
    ATTRIBUTES_FILE = ATTRIBUTES_FILE

    # Environment property keys.
    FILTERS = FILTERS
    OBJECT_SERIALIZERS = OBJECT_SERIALIZERS

    #### 'Context' interface ##################################################

    # The naming environment in effect for this context.
    environment = Dict(ENVIRONMENT)

    # The name of the context within its own namespace.
    namespace_name = Property(Str)

    #### 'PyFSContext' interface ##############################################

    # The name of the context (the last component of the path).
    name = Str

    # The path name of the directory on the local file system.
    path = Str

    #### 'Referenceable' interface ############################################

    # The object's reference suitable for binding in a naming context.
    reference = Property(Instance(Reference))

    #### Private interface ####################################################

    # A mapping from bound name to the name of the corresponding file or
    # directory on the file system.
    _name_to_filename_map = Dict#(Str, Str)

    # The attributes of every object in the context.  The attributes for the
    # context itself have the empty string as the key.
    #
    # {str name : dict attributes}
    #
    # fixme: Don't use 'Dict' here as it causes problems when pickling because
    # trait dicts have a reference back to the parent object (hence we end up
    # pickling all kinds of things that we don't need or want to!).
    _attributes = Any

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **traits):
        """ Creates a new context. """

        # Base class constructor.
        super(PyFSContext, self).__init__(**traits)

        # We cache each object as it is looked up so that all accesses to a
        # serialized Python object return a reference to exactly the same one.
        self._cache = {}

        return

    ###########################################################################
    # 'PyFSContext' interface.
    ###########################################################################

    #### Properties ###########################################################

    def _get_namespace_name(self):
        """ Returns the name of the context within its own namespace. """

        # fixme: clean this up with an initial context API!
        if 'root' in self.environment:
            root = self.environment['root']

            namespace_name = self.path[len(root) + 1:]

        else:
            namespace_name = self.path

        # fixme: This is a bit dodgy 'cos we actually return a name that can
        # be looked up, and not the file system name...
        namespace_name = '/'.join(namespace_name.split(os.path.sep))

        return namespace_name

    #### methods ##############################################################

    def refresh(self):
        """ Refresh the context to reflect changes in the file system. """

        # fixme: This needs more work 'cos if we refresh a context then we
        # will load new copies of serialized Python objects!

        # This causes the initializer to run again the next time the trait is
        # accessed.
        self.reset_traits(['_name_to_filename_map'])

        # Clear out the cache.
        self._cache = {}

        # fixme: This is a bit hacky since the context in the binding may
        # not be None!
        self.context_changed = NamingEvent(
            new_binding=Binding(name=self.name, obj=self, context=None)
        )

        return

    ###########################################################################
    # 'Referenceable' interface.
    ###########################################################################

    #### Properties ###########################################################

    def _get_reference(self):
        """ Returns a reference to this object suitable for binding. """

        abspath = os.path.abspath(self.path)

        reference = Reference(
            class_name = self.__class__.__name__,
            addresses  = [Address(type='pyfs_context', content=abspath)]
        )

        return reference

    ###########################################################################
    # Protected 'Context' interface.
    ###########################################################################

    def _is_bound(self, name):
        """ Is a name bound in this context? """

        return name in self._name_to_filename_map

    def _lookup(self, name):
        """ Looks up a name in this context. """

        if name in self._cache:
            obj = self._cache[name]

        else:
            # Get the full path to the file.
            path = join(self.path, self._name_to_filename_map[name])

            # If the file contains a serialized Python object then load it.
            for serializer in self._get_object_serializers():
                if serializer.can_load(path):
                    try:
                        state = serializer.load(path)

                    # If the load fails then we create a generic file resource
                    # (the idea being that it might be useful to have access to
                    # the file to see what went wrong).
                    except:
                        state = File(path)
                        logger.exception('Error loading resource at %s' % path)

                    break

            # Otherwise, it must just be a file or folder.
            else:
                # Directories are contexts.
                if os.path.isdir(path):
                    state = self._context_factory(name, path)

                # Files are just files!
                elif os.path.isfile(path):
                    state = File(path)

                else:
                    raise ValueError('unrecognized file for %s' % name)

            # Get the actual object from the naming manager.
            obj = naming_manager.get_object_instance(state, name, self)

            # Update the cache.
            self._cache[name] = obj

        return obj

    def _bind(self, name, obj):
        """ Binds a name to an object in this context. """

        # Get the actual state to bind from the naming manager.
        state = naming_manager.get_state_to_bind(obj, name, self)

        # If the object is actually an abstract file then we don't have to
        # do anything.
        if isinstance(state, File):
            if not state.exists:
                state.create_file()

            filename = name

        # Otherwise we are binding an arbitrary Python object, so find a
        # serializer for it.
        else:
            for serializer in self._get_object_serializers():
                if serializer.can_save(obj):
                    path = serializer.save(join(self.path, name), obj)
                    filename = os.path.basename(path)
                    break

            else:
                raise ValueError('cannot serialize object %s' % name)

        # Update the name to filename map.
        self._name_to_filename_map[name] = filename

        # Update the cache.
        self._cache[name] = obj

        return state

    def _rebind(self, name, obj):
        """ Rebinds a name to an object in this context. """

        # We unbind first to make sure that the old file gets removed (this
        # is handy if the object that we are rebinding has a different
        # serializer than the current one).
        #self._unbind(name)

        self._bind(name, obj)

        return

    def _unbind(self, name):
        """ Unbinds a name from this context. """

        # Get the full path to the file.
        path = join(self.path, self._name_to_filename_map[name])

        # Remove it!
        f = File(path)
        f.delete()

        # Update the name to filename map.
        del self._name_to_filename_map[name]

        # Update the cache.
        if name in self._cache:
            del self._cache[name]

        # Remove any attributes.
        if name in self._attributes:
            del self._attributes[name]
            self._save_attributes()

        return

    def _rename(self, old_name, new_name):
        """ Renames an object in this context. """

        # Get the old filename.
        old_filename = self._name_to_filename_map[old_name]
        old_file = File(join(self.path, old_filename))

        # Lookup the object bound to the old name.  This has the side effect
        # of adding the object to the cache under the name 'old_name'.
        obj = self._lookup(old_name)

        # We are renaming a LOCAL context (ie. a folder)...
        if old_file.is_folder:
            # Create the new filename.
            new_filename = new_name
            new_file = File(join(self.path, new_filename))

            # Move the folder.
            old_file.move(new_file)

            # Update the 'Context' object.
            obj.path = new_file.path

            # Update the cache.
            self._cache[new_name] = obj
            del self._cache[old_name]

            # Refreshing the context makes sure that all of its contents
            # reflect the new name (i.e., sub-folders and files have the
            # correct path).
            #
            # fixme: This currently results in new copies of serialized
            # Python objects!  We need to be a bit more judicious in the
            # refresh.
            obj.refresh()

        # We are renaming a file...
        elif isinstance(obj, File):
            # Create the new filename.
            new_filename = new_name
            new_file = File(join(self.path, new_filename))

            # Move the file.
            old_file.move(new_file)

            # Update the 'File' object.
            obj.path = new_file.path

            # Update the cache.
            self._cache[new_name] = obj
            del self._cache[old_name]

        # We are renaming a serialized Python object...
        else:
            # Create the new filename.
            new_filename = new_name + old_file.ext
            new_file = File(join(self.path, new_filename))

            old_file.delete()

            # Update the cache.
            if old_name in self._cache:
                self._cache[new_name] = self._cache[old_name]
                del self._cache[old_name]

            # Force the creation of the new file.
            #
            # fixme: I'm not sure that this is really the place for this.  We
            # do it because often the 'name' of the object is actually an
            # attribute of the object itself, and hence we want the serialized
            # state to reflect the new name... Hmmm...
            self._rebind(new_name, obj)

        # Update the name to filename map.
        del self._name_to_filename_map[old_name]
        self._name_to_filename_map[new_name] = new_filename

        # Move any attributes over to the new name.
        if old_name in self._attributes:
            self._attributes[new_name] = self._attributes[old_name]
            del self._attributes[old_name]
            self._save_attributes()

        return

    def _create_subcontext(self, name):
        """ Creates a sub-context of this context. """

        path = join(self.path, name)

        # Create a directory.
        os.mkdir(path)

        # Create a sub-context that represents the directory.
        sub = self._context_factory(name, path)

        # Update the name to filename map.
        self._name_to_filename_map[name] = name

        # Update the cache.
        self._cache[name] = sub

        return sub

    def _destroy_subcontext(self, name):
        """ Destroys a sub-context of this context. """

        return self._unbind(name)

    def _list_names(self):
        """ Lists the names bound in this context. """

        return list(self._name_to_filename_map.keys())

    # fixme: YFI this is not part of the protected 'Context' interface so
    # what is it doing here?
    def get_unique_name(self, name):

        ext = splitext(name)[1]

        # specially handle '.py' files
        if ext != '.py':
            return super(PyFSContext, self).get_unique_name(name)

        body = splitext(name)[0]
        names = self.list_names()
        i = 2
        unique = name
        while unique in names:
            unique = body + '_' + str(i) + '.py'
            i += 1

        return unique

    ###########################################################################
    # Protected 'DirContext' interface.
    ###########################################################################

    def _get_attributes(self, name):
        """ Returns the attributes of an object in this context. """

        attributes = self._attributes.setdefault(name, {})

        return attributes.copy()

    def _set_attributes(self, name, attributes):
        """ Sets the attributes of an object in this context. """

        self._attributes[name] = attributes
        self._save_attributes()

        return

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _get_filters(self):
        """ Returns the filters for this context. """

        return self.environment.get(self.FILTERS, [])

    def _get_object_serializers(self):
        """ Returns the object serializers for this context. """

        return self.environment.get(self.OBJECT_SERIALIZERS, [])

    def _context_factory(self, name, path):
        """ Create a sub-context. """

        return self.__class__(path=path, environment=self.environment)

    def _save_attributes(self):
        """ Saves all attributes to the attributes file. """

        path = join(self.path, self.ATTRIBUTES_FILE)

        f = open(path, 'wb')
        pickle.dump(self._attributes, f, 1)
        f.close()

        return

    #### Trait initializers ###################################################

    def __name_to_filename_map_default(self):
        """ Initializes the '_name_to_filename' trait. """

        # fixme: We should have a generalized filter mechanism (instead of
        # just 'glob' patterns we should have filter objects that can be a bit
        # more flexible in how they do the filtering).
        patterns = [join(self.path, filter) for filter in self._get_filters()]

        name_to_filename_map = {}
        for filename in os.listdir(self.path):
            path = join(self.path, filename)
            for pattern in patterns:
                if path in glob.glob(pattern):
                    break

            else:
                for serializer in self._get_object_serializers():
                    if serializer.can_load(filename):
                        # fixme: We should probably get the name from the
                        # serializer instead of assuming that we can just
                        # drop the file exension.
                        name, ext = os.path.splitext(filename)
                        break

                else:
                    name = filename

                name_to_filename_map[name] = filename

        return name_to_filename_map

    def __attributes_default(self):
        """ Initializes the '_attributes' trait. """

        attributes_file = File(join(self.path, self.ATTRIBUTES_FILE))
        if attributes_file.is_file:
            f = open(attributes_file.path, 'rb')
            attributes = pickle.load(f)
            f.close()

        else:
            attributes = {}

        return attributes

    #### Trait event handlers #################################################

    def _path_changed(self):
        """ Called when the context's path has changed. """

        basename = os.path.basename(self.path)

        self.name, ext = os.path.splitext(basename)

        return

#### EOF ######################################################################
