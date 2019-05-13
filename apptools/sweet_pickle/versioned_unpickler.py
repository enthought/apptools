#-----------------------------------------------------------------------------
#
#  Copyright (c) 2005-2008 by Enthought, Inc.
#  All rights reserved.
#
#  Author: Dave Peterson <dpeterson@enthought.com>
#  Author: Duncan Child <duncan@enthought.com>
#
#-----------------------------------------------------------------------------
# The code for two-stage unpickling support has been taken from a PEP draft
# prepared by Dave Peterson and Prabhu Ramachandran.

""" An unpickler that is tolerant of class refactorings, and implements a
two-stage pickling process to make it possible to unpickle complicated Python
object hierarchies where the unserialized state of an object depends on the
state of other objects in the same pickle.
"""

# Standard library imports.
import sys
import logging
from os import path
from types import GeneratorType

if sys.version_info[0] >= 3:
    from pickle import _Unpickler as Unpickler
else:
    from pickle import Unpickler

from pickle import UnpicklingError, BUILD

# Enthought library imports
from traits.api import HasTraits, Instance


# Setup a logger for this module
logger = logging.getLogger(__name__)


##############################################################################
# constants
##############################################################################

# The name we backup the original setstate method to.
_BACKUP_NAME = '__enthought_sweet_pickle_original_setstate__'

# The name of the setstate method we hook
_SETSTATE_NAME = '__setstate__'

# The name we store our unpickling data under.
_UNPICKLER_DATA = '__enthought_sweet_pickle_unpickler__'


##############################################################################
# function '__replacement_setstate__'
##############################################################################

def __replacement_setstate__(self, state):
    """ Called to enable an unpickler to modify the state of this instance.
    """
    # Retrieve the unpickling information and use it to let the unpickler
    # modify our state.
    unpickler, module, name = getattr(self, _UNPICKLER_DATA)
    state = unpickler.modify_state(self, state, module, name)

    # If we were given a state, apply it to this instance now.
    if state is not None:

        # Save our state
        logger.debug('Final state: %s', state)
        self.__dict__.update(state)


##############################################################################
# function 'load_build_with_meta_data'
##############################################################################

def load_build_with_meta_data(self):
    """ Called prior to the actual load_build() unpickling method which primes
        the state dictionary with meta-data.
    """

    # Access the state object and check if it is a dictionary (state may also be
    # a tuple, which is used for other unpickling build operations).  Proceed to
    # the standard load_build() if the state obj is not a dict.
    state = self.stack[-1]
    if type(state) == dict:

        # If a file object is used, reference the file name
        if hasattr(self._file, 'name'):
            pickle_file_name = path.abspath(self._file.name)
        else :
            pickle_file_name = ""

        # Add any meta-data needed by __setstate__() methods here...
        state['_pickle_file_name'] = pickle_file_name

    # Call the standard load_build() method
    return self.load_build()


##############################################################################
# class 'NewUnpickler'
##############################################################################
class NewUnpickler(Unpickler):
    """ An unpickler that implements a two-stage pickling process to make it
    possible to unpickle complicated Python object hierarchies where the
    unserialized state of an object depends on the state of other objects in
    the same pickle.
    """

    def load(self, max_pass=-1):
        """Read a pickled object representation from the open file.

        Return the reconstituted object hierarchy specified in the file.
        """
        # List of objects to be unpickled.
        self.objects = []

        # We overload the load_build method.
        dispatch = self.dispatch
        dispatch[BUILD[0]] = NewUnpickler.load_build

        # call the super class' method.
        ret = Unpickler.load(self)
        self.initialize(max_pass)
        self.objects = []

        # Reset the Unpickler's dispatch table.
        dispatch[BUILD[0]] = Unpickler.load_build
        return ret

    def initialize(self, max_pass):
        # List of (object, generator) tuples that initialize objects.
        generators = []

        # Execute object's initialize to setup the generators.
        for obj in self.objects:
            if hasattr(obj, '__initialize__') and \
                   callable(obj.__initialize__):
                ret = obj.__initialize__()
                if isinstance(ret, GeneratorType):
                    generators.append((obj, ret))
                elif ret is not None:
                    raise UnpicklingError('Unexpected return value from '
                        '__initialize__.  %s returned %s' % (obj, ret))

        # Ensure a maximum number of passes
        if max_pass < 0:
            max_pass = len(generators)

        # Now run the generators.
        count = 0
        while len(generators) > 0:
            count += 1
            if count > max_pass:
                not_done = [x[0] for x in generators]
                msg = """Reached maximum pass count %s.  You may have
                         a deadlock!  The following objects are
                         uninitialized: %s""" % (max_pass, not_done)
                raise UnpicklingError(msg)
            for o, g in generators[:]:
                try:
                    next(g)
                except StopIteration:
                    generators.remove((o, g))

    # Make this a class method since dispatch is a class variable.
    # Otherwise, supposing the initial sweet_pickle.load call (which would
    # have overloaded the load_build method) makes a pickle.load call at some
    # point, we would have the dispatch still pointing to
    # NewPickler.load_build whereas the object being passed in will be an
    # Unpickler instance, causing a TypeError.
    @classmethod
    def load_build(cls, obj):
        # Just save the instance in the list of objects.
        if isinstance(obj, NewUnpickler):
            obj.objects.append(obj.stack[-2])
        Unpickler.load_build(obj)


##############################################################################
# class 'VersionedUnpickler'
##############################################################################

class VersionedUnpickler(NewUnpickler, HasTraits):
    """ An unpickler that is tolerant of class refactorings.

        This class reads in a pickled file and applies the transforms
        specified in its updater to generate a new hierarchy of objects
        which are at the current version of the classes they are instances
        of.

        Note that the creation of an updater is kept out of this class to
        ensure that the class can be reused in different situations.
        However, if no updater is provided during construction, then the
        global registry updater will be used.
    """

    ##########################################################################
    # Traits
    ##########################################################################

    ### public 'VersionedUnpickler' interface ################################

    # The updater used to modify the objects being unpickled.
    updater = Instance('apptools.sweet_pickle.updater.Updater')


    ##########################################################################
    # 'object' interface
    ##########################################################################

    ### operator methods #####################################################

    def __init__(self, file, **kws):
        super(VersionedUnpickler, self).__init__(file)

        self._file = file
        if self.updater is None:
            from .global_registry import get_global_registry
            self.updater = get_global_registry()
        logger.debug('VersionedUnpickler [%s] using Updater [%s]', self,
            self.updater)

        # Update the BUILD instruction to use an overridden load_build method
        # NOTE: this is being disabled since, on some platforms, the object
        # is replaced with a regular Unpickler instance, creating a traceback:
        # AttributeError: Unpickler instance has no attribute '_file'
        # ...not sure how this happens since only a VersionedUnpickler has
        # the BUILD instruction replaced with one that uses _file, and it
        # should have _file defined.
        #self.dispatch[BUILD[0]] = load_build_with_meta_data


    ##########################################################################
    # 'Unpickler' interface
    ##########################################################################

    ### public interface #####################################################

    def find_class(self, module, name):
        """ Returns the class definition for the named class within the
            specified module.

            Overridden here to:

            - Allow updaters to redirect to a different class, possibly
              within a different module.
            - Ensure that any setstate hooks for the class are called
              when the instance of this class is unpickled.
        """
        # Remove any extraneous characters that an Unpickler might handle
        # but a user wouldn't have included in their mapping definitions.
        module = module.strip()
        name = name.strip()

        # Attempt to find the class, this may cause a new mapping for that
        # very class to be introduced.  That's why we ignore the result.
        try:
            klass = super(VersionedUnpickler, self).find_class(module, name)
        except:
            pass

        # Determine the target class that the requested class should be
        # mapped to according to our updater.  The target class is the one
        # at the end of any chain of mappings.
        original_module, original_name = module, name
        if self.updater is not None and \
            self.updater.has_class_mapping(module, name):
            module, name = self._get_target_class(module, name)
            if module != original_module or name != original_name:
                logger.debug('Unpickling [%s.%s] as [%s.%s]', original_module,
                    original_name, module, name)

        # Retrieve the target class definition
        try:
            klass = super(VersionedUnpickler, self).find_class(module, name)
        except Exception as e:
            from apptools.sweet_pickle import UnpicklingError
            logger.debug('Traceback when finding class [%s.%s]:' \
                         % (module, name), exc_info=True)
            raise UnpicklingError('Unable to load class [%s.%s]. '
                'Original exception was, "%s".  map:%s' % (
                module, name, str(e), self.updater.class_map))

        # Make sure we run the updater's state functions if any are declared
        # for the target class.
        if self.updater is not None \
            and self._has_state_function(original_module, original_name):
            self._add_unpickler(klass, original_module, original_name)

        return klass


    ##########################################################################
    # 'VersionedUnpickler' interface
    ##########################################################################

    ### public interface #####################################################

    def modify_state(self, obj, state, module, name):
        """ Called to update the specified state dictionary, which represents
            the class of the specified name within the specified module, to
            complete the unpickling of the specified object.
        """
        # Remove our setstate hook and associated data to ensure that
        # instances unpickled through some other framework don't call us.
        # IMPORTANT: Do this first to minimize the time this hook is in place!
        self._remove_unpickler(obj.__class__)

        # Determine what class and version we're starting from and going to.
        # If there is no version information, then assume version 0. (0 is
        # like an unversioned version.)
        source_key = self.updater.get_version_attribute(module, name)
        source_version = state.get(source_key, 0)
        target_key = self.updater.get_version_attribute(
            obj.__class__.__module__, obj.__class__.__name__)
        target_version = getattr(obj, target_key, 0)

        # Iterate through all the updates to the state by going one version
        # at a time.  Note that we assume there is exactly one path from our
        # starting class and version to our ending class and version.  As a
        # result, we assume we update a given class to its latest version
        # before looking for any class mappings.  Note that the version in the
        # updater is the version to convert *TO*.
        version = source_version
        next_version = version + 1
        while True:

            # Iterate through all version updates for the current class.
            key = self.updater.get_version_attribute(module, name)
            while (module, name, next_version) in self.updater.state_functions:
                functions = self.updater.state_functions[(module, name,
                    next_version)]
                for f in functions:
                    logger.debug('Modifying state from [%s.%s (v.%s)] to ' + \
                        '[%s.%s (v.%s)] using function %s', module, name,
                        version, module, name, next_version, f)
                    state = f(state)

                # Avoid infinite loops due to versions not changing.
                new_version = state.get(key, version)
                if new_version == version:
                    new_version = version + 1
                version = new_version
                next_version = version + 1

            # If there is one, move to the next class in the chain.  (We
            # explicitly keep the version number the same.)
            if self.updater.has_class_mapping(module, name):
                original_module, original_name = module, name
                module, name = self.updater.class_map[(module, name)]
                logger.debug('Modifying state from [%s.%s (v.%s)] to ' + \
                    '[%s.%s (v.%s)]', original_module, original_name, version,
                    module, name, version)
            else:
                break

        # If one exists, call the final class's setstate method. According to
        # standard pickling protocol, this method will apply the state to the
        # instance so our state becomes None so that we don't try to apply our
        # unfinished state to the object.
        fn = getattr(obj, _SETSTATE_NAME, None)
        if fn is not None:
            fn(state)
            result = None
            version = getattr(obj, target_key)
        else:
            result = state

        # Something is wrong if we aren't at our target class and version!
        if module != obj.__class__.__module__ \
            or name != obj.__class__.__name__ \
            or version != target_version:
            from apptools.sweet_pickle import UnpicklingError
            raise UnpicklingError('Unexpected state! Got ' + \
                '[%s.%s (v.%s)] expected [%s.%s (v.%s)]' % (module, name,
                version, obj.__class__.__module__, obj.__class__.__name__,
                target_version))

        return result


    ### protected interface ##################################################

    def _add_unpickler(self, klass, module, name):
        """ Modifies the specified class so that our 'modify_state' method
            is called when its next instance is unpickled.
        """
        logger.debug('Adding unpickler hook to [%s]', klass)

        # Replace the existing setstate method with ours.
        self._backup_setstate(klass)
        m = __replacement_setstate__.__get__(None, klass)
        setattr(klass, _SETSTATE_NAME, m)

        # Add the information necessary to allow this unpickler to run
        setattr(klass, _UNPICKLER_DATA, (self, module, name))


    def _backup_setstate(self, klass):
        """ Backs up the specified class's setstate method.
        """
        # We only need to back it up if it actually exists.
        method = getattr(klass, _SETSTATE_NAME, None)
        if method is not None:
            logger.debug('Backing up method [%s] to [%s] on [%s]',
                _SETSTATE_NAME, _BACKUP_NAME, klass)
            m = method.__get__(None, klass)
            setattr(klass, _BACKUP_NAME, m)


    def _get_target_class(self, module, name):
        """ Returns the class info that the class, within the specified module
            and with the specified name, should be instantiated as according to
            our associated updater.

            This is done in a manner that allows for chaining of class mappings
            but is tolerant of the fact that a mapping away from an
            intermediate class may not be registered until an attempt is made
            to load that class.
        """
        # Keep a record of the original class asked for.
        original_module, original_name = module, name

        # Iterate through any mappings in a manner that allows us to detect any
        # infinite loops.
        visited = []
        while self.updater.has_class_mapping(module, name):
            if (module, name) in visited:
                from apptools.sweet_pickle import UnpicklingError
                raise UnpicklingError('Detected infinite loop in class ' + \
                    'mapping from [%s.%s] to [%s.%s] within Updater [%s]' % \
                    (original_module, original_name, module, name,
                    self.updater))
            visited.append( (module, name) )

            # Get the mapping for the current class and try loading the class
            # to ensure any mappings away from it are registered.
            module, name = self.updater.class_map[(module, name)]
            try:
                super(VersionedUnpickler, self).find_class(module, name)
            except:
                logger.exception("_get_target_class can't find: %s" % (module, name))
                pass

        return module, name


    def _has_state_function(self, module, name):
        """ Returns True if the updater contains any state functions that could
            be called by unpickling an instance of the class identified by the
            specified module and name.

            Note: If we had a version number we could tell for sure, but we
            don't have one so we'll have to settle for 'could' be called.
        """
        result = False

        # Iterate through all the class mappings the requested class would
        # go through.  If any of them have a state function, then we've
        # determined our answer and can stop searching.
        #
        # Note we don't need to check for infinite loops because we're only
        # ever called after '_get_target_class' which detects the infinite
        # loops.
        while not result:
            result = self.updater.has_state_function(module, name)
            if not result:
                if self.updater.has_class_mapping(module, name):
                    module, name = self.updater.class_map[(module, name)]
                else:
                    break

        return result


    def _remove_unpickler(self, klass):
        """ Restores the specified class to its unmodified state.  Meaning
            we won't get called when its next instance is unpickled.
        """
        logger.debug('Removing unpickler hook from [%s]', klass)

        # Restore the backed up setstate method
        self._restore_setstate(klass)

        # Remove the unpickling data attached to the class.  This ensures we
        # don't pollute the 'real' attributes of the class.
        delattr(klass, _UNPICKLER_DATA)


    def _restore_setstate(self, klass):
        """ Restores the original setstate method back to its rightful place.
        """
        # We only need to restore if the backup actually exists.
        method = getattr(klass, _BACKUP_NAME, None)
        if method is not None:
            logger.debug('Restoring method [%s] to [%s] on [%s]',
                _BACKUP_NAME, _SETSTATE_NAME, klass)
            delattr(klass, _BACKUP_NAME)
            m = method.__get__(None, klass)
            setattr(klass, _SETSTATE_NAME, m)

        # Otherwise, we simply remove our setstate.
        else:
            delattr(klass, _SETSTATE_NAME)


### EOF ######################################################################

