#-----------------------------------------------------------------------------
#
#  Copyright (c) 2006 by Enthought, Inc.
#  All rights reserved.
#
#  Author: Dave Peterson <dpeterson@enthought.com>
#
#-----------------------------------------------------------------------------

""" Manages a singleton updater that acts as a global registry.

    Our goal is to enable the apptools.sweet_pickle framework to
    understand how pickled data should be treated during unpickling so
    that the resulting object hierarchy reflects the current versions
    of the object's classes -AND- that this should work no matter who
    is doing the unpickling.  This requires a global registry since
    there is no way to know in advance what objects are contained within
    a given pickle file, and thus no way to gather the required
    information to know how to treat the pickle data during unpickling.

    For example, a pickle of an Envisage project may contain many
    custom classes, instantiated at the behest of various plugins,
    which have gone through various versionings and refactorings.  But
    it is the project plugin that needs to unpickle these objects to
    'load' a project, not the other plugins that added those custom
    class instances into the project.


    This registry is used by the apptools.sweet_pickle framework's
    unpickler only by default.   That is, only if no updater was
    explicitly provided.


    It is important that users interact with the registry through the
    provided methods.  If they do not, then the reference they receive
    will be the one that was in place at the time of the import which
    may or MAY NOT be the current repository due to the way this
    framework manages the repository.
"""

try:
    import six.moves._thread as _thread
except ImportError:
    import six.moves._dummy_thread as _thread


##############################################################################
# function 'get_global_registry'
##############################################################################

def get_global_registry():
    """ Returns the global registry in a manner that allows for lazy
        instantiation.
    """
    global _global_registry, _global_registry_lock

    # Do we need to create the registry?
    if _global_registry is None:

        # We can only do this safely in a threaded situation by using a lock.
        # Note that the previous check for None doesn't guarantee we are
        # the only one trying to create an instance, so, we'll check for none
        # again once we acquire the lock and then only create the singleton
        # if there still isn't an instance.
        _global_registry_lock.acquire()
        try:
            if _global_registry is None:
                from .updater import Updater
                _global_registry = Updater()
        finally:
            _global_registry_lock.release()

    return _global_registry


##############################################################################
# private function '_clear_global_registry'
##############################################################################

def _clear_global_registry():
    """ Clears out the current global registry.

        This exists purely to allow testing of the global registry and the
        apptools.sweet_pickle framework.  THIS METHOD SHOULD NEVER BE
        CALLED DURING NORMAL OPERATIONS!
    """
    global _global_registry
    _global_registry = None


##############################################################################
# private, but global, variables
##############################################################################

# The global singleton updater
_global_registry = None

# The lock used to make access to the global singleton thread safe
_global_registry_lock = _thread.allocate_lock()


#### EOF #####################################################################

