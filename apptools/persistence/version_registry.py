"""A version registry that manages handlers for different state
versions.
"""
# Author: Prabhu Ramachandran <prabhu_r@users.sf.net>
# Copyright (c) 2005, Enthought, Inc.
# License: BSD Style.

# Standard library imports.
import sys
import inspect
import logging


logger = logging.getLogger(__name__)


######################################################################
# Utility functions.
######################################################################
def get_version(obj):
    """Walks the class hierarchy and obtains the versions of the
    various classes and returns a list of tuples of the form
    ((class_name, module), version) in reverse order of the MRO.
    """
    res = []
    for cls in inspect.getmro(obj.__class__):
        class_name, module = cls.__name__, cls.__module__
        if module in ['__builtin__']:
            # No point in versioning builtins.
            continue
        try:
            version = cls.__version__
        except AttributeError:
            version = -1
        res.append( ( (class_name, module), version) )
    res.reverse()
    return res


######################################################################
# `HandlerRegistry` class.
######################################################################
class HandlerRegistry:
    """A simple version conversion handler registry.  Classes register
    handlers in order to convert the state version to the latest
    version.  When an object's state is about to be set, the `update`
    method of the registy is called.  This in turn calls any handlers
    registered for the class/module and this handler is then called
    with the state and the version of the state.  The state is
    modified in-place by the handlers.
    """

    def __init__(self):
        # The version conversion handlers.
        # Key: (class_name, module), value: handler
        self.handlers = {}

    def register(self, class_name, module, handler):
        """Register `handler` that handles versioning for class having
        class name (`class_name`) and module name (`module`).  The
        handler function will be passed the state and its version to fix.
        """
        key = (class_name, module)
        if key in self.handlers:
            msg = 'Overwriting version handler for (%s, %s)'%(key[0], key[1])
            logger.warn(msg)
        self.handlers[(class_name, module)] = handler

    def unregister(self, class_name, module):
        """Unregisters any handlers for a class and module.
        """
        self.handlers.pop((class_name, module))

    def update(self, state):
        """Updates the given state using the handlers.  Note that the
        state is modified in-place.
        """
        if (not self.handlers) or  (not hasattr(state, '__metadata__')):
            return
        versions = state.__metadata__['version']
        for ver in versions:
            key = ver[0]
            try:
                self.handlers[key](state, ver[1])
            except KeyError:
                pass


def _create_registry():
    """Creates a reload safe, singleton registry.
    """
    registry = None
    for key in sys.modules.keys():
        if 'version_registry' in key:
            mod = sys.modules[key]
            if hasattr(mod, 'registry'):
                registry = mod.registry
                break
    if not registry:
        registry = HandlerRegistry()
    return registry


# The singleton registry.
registry = _create_registry()

