#-----------------------------------------------------------------------------
#
#  Copyright (c) 2005, 2006 by Enthought, Inc.
#  All rights reserved.
#
#  Author: Dave Peterson <dpeterson@enthought.com>
#  Author: Duncan Child <duncan@enthought.com>
#
#-----------------------------------------------------------------------------

""" A record of refactorings to be performed during unpickling of objects.
"""

# Standard library imports
import logging

# Enthought library imports
from traits.api import Dict, HasPrivateTraits, Int, List, Tuple, Str


logger = logging.getLogger(__name__)


##############################################################################
# class 'Updater'
##############################################################################

class Updater(HasPrivateTraits):
    """ A record of refactorings to be performed during unpickling of objects.
    """

    ##########################################################################
    # Traits
    ##########################################################################

    ### public 'Updater' interface ###########################################

    # Mappings from a pickled class to a class it should be unpickled as.
    #
    # The keys are a tuple of the source class's module and class names in
    # that order.  The values are the target class's module and class names
    # in that order.
    class_map = Dict(Tuple(Str, Str), Tuple(Str, Str))

    # State functions that should be called to convert state from one version
    # of a class to another.
    #
    # The keys are a tuple of the class's module name, class name, and version
    # in that order.  The values are a list of functions to be called during
    # unpickling to do the state conversion.   Note that the version in the
    # key represents the version that the function converts *TO*.
    state_functions = Dict(Tuple(Str, Str, Int), List)

    # Our record of the attribute that records the version number for a
    # specific class.  If no record is found for a given class, then the
    # default value is used instead -- see '_default_version_attribute'.
    #
    # The key is a tuple of the class's module name and class name in that
    # order.  The value is the name of the version attribute.
    version_attribute_map = Dict(Tuple(Str, Str), Str)


    ### protected 'Updater' interface ########################################

    # The default name of the attribute that declares the version of a class
    # or class instance.
    _default_version_attribute = '_enthought_pickle_version'

    # A record of which classes we have state functions for.
    #
    # The keys are a tuple of the class's module name and class name in that
    # order.  The values are reference counts.
    _state_function_classes = Dict(Tuple(Str, Str), Int)


    ##########################################################################
    # 'Updater' interface
    ##########################################################################

    ### public interface #####################################################

    def add_mapping(self, source_module, source_name, target_module,
        target_name):
        """ Adds a mapping from the class with the source name in the source
            module to the class with the target name in the target module.
        """
        self.class_map[(source_module, source_name)] = (target_module,
            target_name)


    def add_mapping_to_class(self, source_module, source_name, target_class):
        """ Convenience method to add a mapping, from the class with the
            source name in the source module to the target class.
        """
        self.add_mapping(source_module, source_name, target_class.__module__,
            target_class.__name__)


    def add_mappings(self, source_module, target_module, class_names):
        """ Adds mappings, from the specified source module to the specified
            target module, for each of the class names in the specified
            list.
        """
        for name in class_names:
            self.add_mapping(source_module, name, target_module, name)


    def add_state_function(self, module, name, target_version, function):
        """ Adds the specified function as a state function to be called to
            convert an instance of the class with the specified name within
            the specified module *TO* the specified version.

            Note that the framework handles calling of state functions to make
            the smallest version jumps possible.
        """
        key = (module, name, target_version)
        list = self.state_functions.setdefault(key, [])
        list = list[:] # Copy necessary because traits only recognizes list
                       # changes by list instance - not its contents.
        list.append(function)
        self.state_functions[key] = list


    def add_state_function_for_class(self, klass, target_version, function):
        """ Convenience method to add the specified function as a state
            function to be called to convert an instance of the specified
            class *TO* the specified version.
        """
        self.add_state_function(klass.__module__, klass.__name__,
            target_version, function)


    def declare_version_attribute(self, module, name, attribute_name):
        """ Adds the specified attribute name as the version attribute for the
            class within the specified module with the specified name.
        """
        self.version_attribute_map[(module, name)] = attribute_name


    def declare_version_attribute_for_class(self, klass, attribute_name):
        """ Covenience method to add the specified attribute name as the
            version attribute for the specified class.
        """
        self.declare_version_attribute(klass.__module__, klass.__name__,
            attribute_name)


    def get_version_attribute(self, module, name):
        """ Returns the name of the version attribute for the class of the
            specified name within the specified module.
        """
        return self.version_attribute_map.get( (module, name),
            self._default_version_attribute)


    def has_class_mapping(self, module, name):
        """ Returns True if this updater contains a class mapping for
            the class identified by the specified module and class name.
        """
        return (module, name) in self.class_map


    def has_state_function(self, module, name):
        """ Returns True if this updater contains any state functions for
            the class identified by the specified module and class name.
        """
        return (module, name) in self._state_function_classes


    def merge_updater(self, updater):
        """ Merges the mappings and state functions from the specified updater
            into this updater.
        """
        self.class_map.update(updater.class_map)
        self.version_attribute_map.update(updater.version_attribute_map)

        # The state functions dictionary requires special processing because
        # each value is a list and we don't just want to replace the existing
        # list with only the new content.
        for key, value in updater.state_functions.items():
            if isinstance(value, list) and len(value) > 0:
                funcs = self.state_functions.setdefault(key, [])
                funcs = funcs[:] # Copy necessary because traits only recognizes
                               # funcs changes by funcs instance - not its
                               # contents.
                funcs.extend(value)
                self.state_functions[key] = funcs


    ### trait handlers #######################################################

    def _class_map_changed(self, old, new):
        logger.debug('Detected class_map change from [%s] to [%s] in [%s]',
            old, new, self)


    def _class_map_items_changed(self, event):
        for o in event.removed:
            logger.debug('Detected [%s] removed from class_map in [%s]', o,
                self)
        for k, v in event.changed.items():
            logger.debug('Detected [%s] changed from [%s] to [%s] in ' + \
                'class_map in [%s]', k, v, self.class_map[k], self)
        for k, v in event.added.items():
            logger.debug('Detected mapping from [%s] to [%s] added to ' + \
                'class_map in [%s]', k, v, self)


    def _state_functions_changed(self, old, new):
        logger.debug('Detected state_functions changed from [%s] to [%s] ' + \
            'in [%s]', old, new, self)

        # Update our record of which classes we have state functions for.
        # All of our old state functions are gone so we simply need to rescan
        # the new functions.
        self._state_function_classes.clear()
        for key, value in new.items():
            module, name, version = key
            klass_key = (module, name)
            count = self._state_function_classes.setdefault(klass_key, 0)
            self._state_function_classes[klass_key] = count + len(value)


    def _state_functions_items_changed(self, event):
        # Decrement our reference counts for the classes we no longer
        # have state functions for.  If the reference count reaches zero,
        # remove the record completely.
        for k, v in event.removed.items():
            logger.debug('Detected [%s] removed from state_functions in [%s]',
                k, self)

            # Determine the new reference count of state functions for the
            # class who the removed item was for.
            module, name, version = k
            key = (module, name)
            count = self._state_function_classes[key] - len(v)

            # Store the new reference count.  Delete the entry if it is zero.
            if count < 0:
                logger.warn('Unexpectedly reached negative reference count ' +
                    'value of [%s] for [%s]', count, key)
                del self._state_function_classes[key]
            elif count == 0:
                del self._state_function_classes[key]
            else:
                self._state_function_classes[key] = count

        # Update our reference counts for changes to the list of functions
        # for a specific class and version.  The 'changed' dictionary's values
        # are the old values.
        for k, v in event.changed.items():
            value = self.state_functions[k]
            logger.debug('Detected [%s] changed in state_functions from ' + \
                '[%s] to [%s] in [%s]', k, v, value, self)

            # Determine the new reference count as a result of the change.
            module, name, version = k
            key = (module, name)
            count = self._state_function_classes[key] - len(v) + len(value)

            # Store the new reference count.  Delete the entry if it is zero.
            if count < 0:
                logger.warn('Unexpectedly reached negative reference count ' +
                    'value of [%s] for [%s]', count, key)
                del self._state_function_classes[key]
            elif count == 0:
                del self._state_function_classes[key]
            else:
                self._state_function_classes[key] = count


        # Update our reference counts for newly registered state functions.
        for k, v in event.added.items():
            logger.debug('Detected mapping of [%s] to [%s] added to ' + \
                'state_functions in [%s]', k, v, self)

            # Determine the new reference count as a result of the change.
            module, name, version = k
            key = (module, name)
            count = self._state_function_classes.setdefault(key, 0) + len(v)

            # Store the new reference count
            self._state_function_classes[key] = count


    def _version_attribute_map_changed(self, old, new):
        logger.debug('Detected version_attribute_map change from [%s] ' + \
            'to [%s] in [%s]', old, new, self)


    def _version_attribute_map_items_changed(self, event):
        for o in event.removed:
            logger.debug('Detected [%s] removed from version_attribute_map ' + \
                'in [%s]', o, self)
        for o in event.changed:
            logger.debug('Detected [%s] changed in version_attribute_map ' + \
                'in [%s]', o, self)
        for o in event.added:
            logger.debug('Detected [%s] added to version_attribute_map in ' + \
                '[%s]', o, self)


### EOF ######################################################################
