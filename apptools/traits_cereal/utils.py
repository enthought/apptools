#!/usr/bin/env python
# -*- coding: utf-8 -*-

from traits.trait_handlers import (
    TraitDictObject, TraitListObject, TraitSetObject)


def class_qualname(obj):
    obj = get_obj_of_type(obj)
    return '.'.join([obj.__class__.__module__, obj.__class__.__name__])


def get_obj_of_type(obj):
    """Return an object of the type of this object.

    `TraitTypeObject`s screw up our type checking, so we drop them down to
    their primitive types here, otherwise we just return the object itself."""
    type_ = TYPE_MAP.get(type(obj))
    if type_ is not None:
        obj = type_(obj)
    return obj

TYPE_MAP = {
    TraitListObject: list,
    TraitDictObject: dict,
    TraitSetObject: set,
}
