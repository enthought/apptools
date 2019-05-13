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


# Standard library imports.
import inspect
import types

# Enthought library imports.
from traits.api import HasTraits

# Local imports.
from .package_globals import get_script_manager
from .scriptable import scriptable, Scriptable


def create_scriptable_type(scripted_type, name=None, bind_policy='auto',
        api=None, includes=None, excludes=None, script_init=True):
    """Create and return a new type based on the given scripted_type that will
    (by default) have its public methods and traits (ie. those not beginning
    with an underscore) made scriptable.

    name is the name that objects of this type will be bound to.  It defaults
    to the name of scripted_type with the first character forced to lower case.
    It is ignored if script_init is False.

    bind_policy determines what happens if a name is already bound.  If the
    policy is 'auto' then a numerical suffix will be added to the name, if
    necessary, to make it unique.  If the policy is 'unique' then an exception
    is raised.  If the policy is 'rebind' then the previous binding is
    discarded.  It is ignored if script_init is False.  The default is 'auto'.

    If api is given then it is a class, or a list of classes, that define the
    attributes that will be made scriptable.

    Otherwise if includes is given it is a list of names of attributes that
    will be made scriptable.

    Otherwise all the public attributes of scripted_type will be made
    scriptable except those in the excludes list.

    Irrespective of any other arguments, if script_init is set then the
    __init__() method will always be made scriptable.
    """

    def __init__(self, *args, **kwargs):
        """Initialise the dynamic sub-class instance."""

        get_script_manager().new_object(self, scripted_type, args, kwargs,
                name, bind_policy)
        scripted_type.__init__(self, *args, **kwargs)

    # See if we need to pull all attribute names from a type.
    if api is not None:
        if isinstance(api, list):
            src = api
        else:
            src = [api]
    elif includes is None:
        src = [scripted_type]
    else:
        names = includes
        src = None

    if src:
        ndict = {}

        for cls in src:
            if issubclass(cls, HasTraits):
                for n in cls.class_traits().keys():
                    if not n.startswith('_') and not n.startswith('trait'):
                        ndict[n] = None

            for c in inspect.getmro(cls):
                if c is HasTraits:
                    break

                for n in c.__dict__.keys():
                    if not n.startswith('_'):
                        ndict[n] = None

        # Respect the excludes so long as there was no explicit API.
        if api is None and excludes is not None:
            for n in excludes:
                try:
                    del ndict[n]
                except KeyError:
                    pass

        names = list(ndict.keys())

    # Create the type dictionary containing replacements for everything that
    # needs to be scriptable.
    type_dict = {}
    if script_init:
        type_dict['__init__'] = __init__

    if issubclass(scripted_type, HasTraits):
        traits = scripted_type.class_traits()

        for n in names:
            trait = traits.get(n)

            if trait is not None:
                type_dict[n] = Scriptable(trait)

    for n in names:
        try:
            attr = getattr(scripted_type, n)
        except AttributeError:
            continue

        if type(attr) is types.MethodType:
            type_dict[n] = scriptable(attr)

    type_name = 'Scriptable(%s)' % scripted_type.__name__

    return type(type_name, (scripted_type, ), type_dict)


def make_object_scriptable(obj, api=None, includes=None, excludes=None):
    """Make (by default) an object's public methods and traits (ie. those not
    beginning with an underscore) scriptable.

    If api is given then it is a class, or a list of classes, that define the
    attributes that will be made scriptable.

    Otherwise if includes is given it is a list of names of attributes that
    will be made scriptable.

    Otherwise all the public attributes of scripted_type will be made
    scriptable except those in the excludes list.
    """

    # Create the new scriptable type.
    new_type = create_scriptable_type(obj.__class__, api=api,
            includes=includes, excludes=excludes, script_init=False)

    # Fix the object's type to make it scriptable.
    obj.__class__ = new_type
