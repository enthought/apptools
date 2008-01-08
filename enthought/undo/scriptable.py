#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Riverbank Computing Limited
# Description: <Enthought undo package component>
#------------------------------------------------------------------------------


# Enthought library imports.
from enthought.traits.api import Any, Property, Undefined
from enthought.traits.traits import trait_cast

# Local imports.
from script_manager import ScriptManager
from scriptable_object import ScriptableObject


# This is the guard that ensures that only outermost scriptable methods get
# recorded.
_outermost_call = True


def scriptable(func):
    """ This is the decorator applied to methods of objects that sub-class
    ScriptableObject to mark them as being scriptable.
    """

    def _scripter(*args, **kwargs):
        """ This is the wrapper that is returned in place of the scriptable
        method.
        """

        if len(args) == 0 or not isinstance(args[0], ScriptableObject):
            raise TypeError, "the scriptable decorator can only be applied to methods of objects that sub-class ScriptableObject"

        global _outermost_call

        if _outermost_call:
            _outermost_call = False

            # See if there is an undo manager set.
            undo_manager = args[0].undo_manager

            if undo_manager is None:
                # This could either be because __init__ has been decorated or
                # we are running a recorded script.
                if func.func_name == '__init__':
                    ScriptManager.new_object(args[0], args[1:], kwargs)

                try:
                    result = func(*args, **kwargs)
                finally:
                    _outermost_call = True
            else:
                # Record the ordinary method.
                try:
                    result = undo_manager.record_method(func, args, kwargs)
                finally:
                    _outermost_call = True
        else:
            # We aren't at the outermost call so just invoke the method.
            result = func(*args, **kwargs)

        return result

    # Be a good citizen.
    _scripter.__name__ = func.__name__
    _scripter.__doc__ = func.__doc__
    _scripter.__dict__.update(func.__dict__)

    return _scripter


def _scriptable_get(obj, name):
    """ The getter for a scriptable trait. """

    if not isinstance(obj, ScriptableObject):
        raise TypeError, "a Scriptable trait can only be contained in objects that sub-class ScriptableObject"

    global _outermost_call

    saved_outermost = _outermost_call
    _outermost_call = False

    try:
        result = getattr(obj, '_' + name, None)

        if result is None:
            result = obj.trait(name).default
    finally:
        _outermost_call = saved_outermost

    if saved_outermost and obj.undo_manager is not None:
        obj.undo_manager.record_trait_get(obj, name, result)

    return result


def _scriptable_set(obj, name, value):
    """ The setter for a scriptable trait. """

    if not isinstance(obj, ScriptableObject):
        raise TypeError, "a Scriptable trait can only be contained in objects that sub-class ScriptableObject"

    if _outermost_call and obj.undo_manager is not None:
        obj.undo_manager.record_trait_set(obj, name, value)

    _name = '_' + name
    old_value = getattr(obj, _name, Undefined)

    if old_value is not value:
        setattr(obj, _name, value)
        obj.trait_property_changed(name, old_value, value)


def Scriptable(trait=Any, **metadata):
    """ Scriptable is a wrapper around another trait that makes it scriptable,
    ie. changes to its value can be recorded.  If a trait is read, but the
    value isn't set to another scriptable trait or passed to a scriptable
    method then the read will not be included in the recorded script.  To make
    sure a read is always recorded set the 'has_side_effects' argument to True.
    """

    trait = trait_cast(trait)
    metadata['default'] = trait.default_value()[1]

    return Property(_scriptable_get, _scriptable_set, trait=trait, **metadata)
