#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import uuid

from traits.api import HasTraits, Instance
from traits.adaptation.adapter import Adapter

from .blob import Blob, blob_skeleton
from .utils import get_obj_of_type


class DefaultDeflator(Adapter):
    version = 1
    adaptee = Instance(HasTraits)

    def deflate(self, get_or_create_uuid):
        children = set()

        obj_attrs = self.adaptee.__getstate__()
        obj_attrs.pop('__traits_version__')
        # Go through the attr dict and replace objects with uuids as needed
        for attr, val in obj_attrs.items():
            obj_attrs[attr], more_children = deflate(val, get_or_create_uuid)
            children |= more_children

        return blob_skeleton(
            self.adaptee,
            get_or_create_uuid,
            obj_attrs=obj_attrs,
            children=children)


class DefaultInflator(Adapter):
    version = 1
    adaptee = Instance(Blob)

    # IInflatable #########################################################

    def inflate(self, get_obj_by_uuid, reify=True):
        blob = self.adaptee

        # FIXME: we'd like to pass `reify` down recursively and avoid
        # instantiating *anything* yet, but does it even make sense to call
        # this method in such a case?

        # Go through the attr dict and replace uuids with objects as needed
        blob.obj_attrs = inflate(
            blob.obj_attrs, get_obj_by_uuid)
        #    blob.obj_attrs, partial(get_obj_by_uuid, reify=reify))

        return blob if not reify else reify_blob(blob)


def reify_blob(blob):
    modpath, clsname = blob.class_name.rsplit('.', 1)
    mod = __import__(modpath, fromlist=[clsname])
    klass = getattr(mod, clsname)
    return klass(**blob.obj_attrs)


def is_deflatable(obj):
    # FIXME: We can put whatever we want here to detect deflatat akkkjjbles.
    return isinstance(obj, HasTraits)


def is_inflatable(obj):
    return isinstance(obj, uuid.UUID)


def _deflate_collection(collection, get_or_create_uuid):
    collection = get_obj_of_type(collection)
    new = []
    children = set()
    for o in collection:
        res, more_children = deflate(o, get_or_create_uuid)
        new.append(res)
        children |= more_children
    ret = type(collection)(new)
    return ret, children


def _inflate_collection(collection, get_obj_by_uuid):
    collection = get_obj_of_type(collection)
    new = [inflate(obj, get_obj_by_uuid) for obj in collection]
    ret = type(collection)(new)
    return ret


def _deflate_mapping(mapping, get_or_create_uuid):
    if mapping:
        mapping = get_obj_of_type(mapping)
        keys, values = zip(*mapping.items())
        keys, children = _deflate_collection(keys, get_or_create_uuid)
        values, more_children = _deflate_collection(values, get_or_create_uuid)
        children |= more_children
        ret = type(mapping)(zip(keys, values))
        return ret, children
    else:
        return mapping, set()


def _inflate_mapping(mapping, get_obj_by_uuid):
    mapping = get_obj_of_type(mapping)
    if mapping:
        keys, values = zip(*mapping.items())
        keys = _inflate_collection(keys, get_obj_by_uuid)
        values = _inflate_collection(values, get_obj_by_uuid)
        ret = type(mapping)(zip(keys, values))
        return ret
    else:
        return mapping


def deflate(obj, get_or_create_uuid):
    """ Return a Tuple(Any, Set) representing the deflated version of this
    object or container and a set of chlid objects which must also be deflated.

    The Any is expected to be some primitive type that is directly storable
    as a value or a ``uuid.UUID`` object representing the serialization
    of this object elsewhere or a container of some combination of those.
    """
    obj = get_obj_of_type(obj)
    # By default, assume it's a primitive value to be saved directly
    # If we determine later that it isn't, we'll replace it with its UUID
    # and schedule it for saving
    ret = obj
    children = set()

    # Poor man's pattern matching...
    # Not a container
    if is_deflatable(obj):
        ret = get_or_create_uuid(obj)
        children.add(obj)

    # Normal iterable containers
    elif isinstance(obj, (set, tuple, list)):
        return _deflate_collection(obj, get_or_create_uuid)

    # Mapping style containers
    elif isinstance(obj, dict):
        return _deflate_mapping(obj, get_or_create_uuid)

    return ret, children


def inflate(obj, get_obj_by_uuid):
    """ Return a fully inflated (but not instantiated) object if obj is a UUID.
    Otherwise return obj.

    Containers have their UUID contents replaced with objects as well.
    """
    # By default, assume it's a primitive value to be returned directly
    # If we determine later that it's a UUID we'll replace it with its
    # instantiated object
    ret = obj

    # Poor man's pattern matching...
    # Not a container
    if is_inflatable(obj):
        ret = get_obj_by_uuid(obj)

    # Normal iterable containers
    elif isinstance(obj, (set, tuple, list)):
        ret = _inflate_collection(obj, get_obj_by_uuid)

    # Mapping style containers
    elif isinstance(obj, dict):
        ret = _inflate_mapping(obj, get_obj_by_uuid)

    return ret
