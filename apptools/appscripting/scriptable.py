#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Riverbank Computing Limited
# Description: <Enthought application scripting package component>
#------------------------------------------------------------------------------


# Enthought library imports.
from traits.api import Any, Property, Undefined
from traits.traits import trait_cast

# Local imports.
from .package_globals import get_script_manager


# This is the guard that ensures that only outermost scriptable methods get
# recorded.
_outermost_call = True


def scriptable(func):
    """ This is the decorator applied to functions and methods to mark them as
    being scriptable.
    """

    def _scripter(*args, **kwargs):
        """ This is the wrapper that is returned in place of the scriptable
        method.
        """

        global _outermost_call

        if _outermost_call:
            _outermost_call = False

            # See if there is an script manager set.
            sm = get_script_manager()

            if func.__name__ == '__init__':
                sm.new_object(args[0], type(args[0]), args[1:], kwargs)

                try:
                    result = func(*args, **kwargs)
                finally:
                    _outermost_call = True
            else:
                # Record the ordinary method.
                try:
                    result = sm.record_method(func, args, kwargs)
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

    global _outermost_call

    saved_outermost = _outermost_call
    _outermost_call = False

    try:
        result = getattr(obj, '_' + name, None)

        if result is None:
            result = obj.trait(name).default
    finally:
        _outermost_call = saved_outermost

    if saved_outermost:
        get_script_manager().record_trait_get(obj, name, result)

    return result


def _scriptable_set(obj, name, value):
    """ The setter for a scriptable trait. """

    if _outermost_call:
        get_script_manager().record_trait_set(obj, name, value)

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
