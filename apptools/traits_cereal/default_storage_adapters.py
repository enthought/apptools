#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

from functools import partial
import uuid

from traits.api import HasTraits, Instance, Constant
from traits.adaptation.adapter import Adapter

from .blob import Blob, blob_skeleton
from .interfaces import IDeflatable, IInflatable
from .utils import get_obj_of_type


class DefaultDeflator(Adapter, IDeflatable):

    """ The default implementation of the IDeflatable protocol. """

    #: The version of the deflation algorithm used
    version = Constant(1)

    #: The object that is being adapted to IDeflatable
    adaptee = Instance(HasTraits)

    def deflate(self, get_key):
        """ Return the `Blob` that represents the deflated adaptee.

        Params:

        get_key(obj) : Callable
            A callable which returns the appropriate key for its argument.
        """

        children = set()
        obj_attrs = {}

        if self.adaptee:
            obj_attrs.update(self.adaptee.__getstate__())
            obj_attrs.pop('__traits_version__')
            # Go through the attr dict and replace objects with keys as needed
            for attr, val in obj_attrs.items():
                obj_attrs[attr], more_children = deflate(val, get_key)
                children |= more_children

        return blob_skeleton(
            self.adaptee,
            get_key,
            obj_attrs=obj_attrs,
            children=children)


class DefaultInflator(Adapter, IInflatable):

    """ The default implementation of the IInflatable protocol. """

    #: The version of the deflation algorithm that this inflator expects
    version = 1

    #: The `Blob` that is being adapted to IInflatable
    adaptee = Instance(Blob)

    def inflate(self, get_obj_by_key, reify=True):
        """ Inflate this intermediate object into an instance of its original
        type.

        In general, `reify` should only be False when using inflate as an
        intermediate step (possibly due to subclassing), otherwise assumptions
        about object identity when retrieving from storage may not hold.

        Params:

        get_obj_by_key(key, reify=reify) : callable
            A callable which returns the object associated with `key` from the
            data store.

        reify : bool
            If reify is True, return the fully instantiated object that the
            adaptee Blob represents.
            Otherwise, return a `Blob` with the set of children populated with
            the necessary child Blobs.

        """

        blob = self.adaptee

        # Go through the attr dict and replace keys with objects as needed
        blob.obj_attrs = inflate(
            blob.obj_attrs, partial(get_obj_by_key, reify=reify))

        return blob if not reify else reify_blob(blob)


### Object deflation/inflation helpers ########################################

def reify_blob(blob):
    """ Return an instance of the same class as the object that was deflated
    to create this blob. """
    modpath, clsname = blob.class_name.rsplit('.', 1)
    mod = __import__(modpath, fromlist=[clsname])
    klass = getattr(mod, clsname)
    return klass(**blob.obj_attrs)


def deflate(obj, get_key):
    """ Return a Tuple(Any, Set) representing the deflated version of
    this object or container and a set of chlid objects which must also
    be deflated.

    The Any is expected to be some primitive type that is directly
    storable as a value or a ``uuid.UUID`` object or arbitrary string
    representing the serialization of this object elsewhere or a
    container of some combination of those.
    """
    obj = get_obj_of_type(obj)
    # By default, assume it's a primitive value to be saved directly
    # If we determine later that it isn't, we'll replace it with its key
    # and schedule it for saving
    ret = obj
    children = set()

    # Poor man's pattern matching...
    # Not a container
    if is_deflatable(obj):
        ret = get_key(obj)
        children.add(obj)

    # Normal iterable containers
    elif isinstance(obj, (set, tuple, list)):
        return _deflate_iterable(obj, get_key)

    # Mapping style containers
    elif isinstance(obj, dict):
        return _deflate_mapping(obj, get_key)

    return ret, children


def inflate(obj, get_obj_by_key):
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
        ret = get_obj_by_key(obj)

    # Normal iterable containers
    elif isinstance(obj, (set, tuple, list)):
        ret = _inflate_iterable(obj, get_obj_by_key)

    # Mapping style containers
    elif isinstance(obj, dict):
        ret = _inflate_mapping(obj, get_obj_by_key)

    return ret


def is_deflatable(obj):
    """ Return true if we should attempt to deflate `obj`. """
    # FIXME: We can put whatever we want here to detect deflatables.
    return isinstance(obj, HasTraits)


def is_inflatable(obj):
    """ Return true if we should attempt to inflate `obj`. """
    return isinstance(obj, uuid.UUID)


def _deflate_iterable(iterable, get_key):
    """ Replace deflatable objects in `iterable` with their deflated versions.
    """
    iterable = get_obj_of_type(iterable)
    new = []
    children = set()
    for o in iterable:
        res, more_children = deflate(o, get_key)
        new.append(res)
        children |= more_children
    ret = type(iterable)(new)
    return ret, children


def _inflate_iterable(iterable, get_obj_by_key):
    """ Replace inflatable objects in `iterable` with their inflated versions.
    """
    iterable = get_obj_of_type(iterable)
    new = [inflate(obj, get_obj_by_key) for obj in iterable]
    ret = type(iterable)(new)
    return ret


def _deflate_mapping(mapping, get_key):
    """ Replace deflatable keys and values in `mapping` with their deflated
    versions. """
    if mapping:
        mapping = get_obj_of_type(mapping)
        keys, values = zip(*mapping.items())
        keys, children = _deflate_iterable(keys, get_key)
        values, more_children = _deflate_iterable(values, get_key)
        children |= more_children
        ret = type(mapping)(zip(keys, values))
        return ret, children
    else:
        return mapping, set()


def _inflate_mapping(mapping, get_obj_by_key):
    """ Replace inflatable keys and values in `mapping` with their inflated
    versions. """
    mapping = get_obj_of_type(mapping)
    if mapping:
        keys, values = zip(*mapping.items())
        keys = _inflate_iterable(keys, get_obj_by_key)
        values = _inflate_iterable(values, get_obj_by_key)
        ret = type(mapping)(zip(keys, values))
        return ret
    else:
        return mapping
