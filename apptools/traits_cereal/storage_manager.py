#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import collections
from uuid import uuid4
from weakref import WeakKeyDictionary, WeakValueDictionary

from traits.api import Bool, HasStrictTraits, Instance, Supports
from traits.adaptation.adaptation_manager import (
    AdaptationManager, get_global_adaptation_manager)

from .default_storage_adapters import DefaultDeflator, DefaultInflator
from .hdf5_object_store import HDF5ObjectStore
from .interfaces import IObjectStore, IDeflatable, IInflatable


import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8.8s [%(name)s:%(lineno)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level='DEBUG')
logger = logging.getLogger(__name__)


class WeakRefCache(collections.MutableMapping):

    """A cache that stores keys by strong reference, but values by weakref,
    while maintaining quick lookup of both values and keys."""

    def __init__(self):
        self._value_to_key = WeakKeyDictionary()
        self._key_to_value = WeakValueDictionary()

    def __contains__(self, key):
        self._sanity_check()
        return key in self._value_to_key or key in self._key_to_value

    def __setitem__(self, key, val):
        self._sanity_check()
        self._key_to_value[key] = val
        self._value_to_key[val] = key

    def __getitem__(self, key):
        self._sanity_check()
        return self._key_to_value.get(key)

    def setdefault(self, key, default=None):
        value = self._key_to_value.setdefault(key, default)
        self._value_to_key[value] = key
        return value

    def setdefault_by_value(self, value, default=None):
        key = self._value_to_key.setdefault(value, default)
        self._key_to_value[key] = value
        return key

    def get(self, key, default=None):
        self._sanity_check()
        return self._key_to_value.get(key, default)

    def get_by_value(self, value, default=None):
        """ Return the key associated with the given value. """
        self._sanity_check()
        return self._value_to_key.get(value, default)

    def __len__(self):
        self._sanity_check()
        return len(self._value_to_key)

    def __delitem__(self, key):
        self._sanity_check()
        val = self._key_to_value[key]
        del self._key_to_value[key]
        del self._value_to_key[val]

    def __iter__(self):
        self._sanity_check()
        return iter(self.data.keys())

    def _sanity_check(self):
        left = dict(self._value_to_key.items())
        right = {v: k for k, v in self._key_to_value.items()}
        assert left == right

    def clear(self):
        """ DANGER!!! Clear everything out of the cache.

        This is mainly for testing purposes, but can be useful to force
        reloading valueects from cold storage.
        """
        self._value_to_key.clear()
        self._key_to_value.clear()


class StorageManager(HasStrictTraits):

    """ A manager for objects that must be sent to remote storage.

    By default, it uses an YAML-in-HDF5 backend, but supports any
    backend that can be adapted to `interfaces.IObjectStore`.

    All objects exposing `__getstate__` can be stored using
    a default deflation algorithm that tries to preserve as much
    information about the object as possible. Objects which only
    require storing part of their state should have their own
    adapters to `IDeflatable`.

    Access to the underlying storage layer is cached using
    `WeakRefCache`. As such, the StorageManager guarantees that
    any attempt to load an already-existant object will immediately
    return a reference to that same object instance.

    """

    #: The adaptation manager used to adapt storable objects
    adaptation_manager = Instance(AdaptationManager)

    #: The backend used to marshall objects to and from storage
    store = Supports(IObjectStore)

    #: The caching layer between storage and application
    _cache = Instance(WeakRefCache, WeakRefCache)

    #: Whether to use the default deflator
    use_default = Bool(True)

    def _adaptation_manager_default(self):
        return get_global_adaptation_manager()

    def _store_default(self):
        return HDF5ObjectStore()

    def save(self, obj, key=None):
        if obj is None:
            return None
        return self._save(key, obj, set())

    def _save(self, key, obj, saved_objects):
        if obj in saved_objects:
            logger.debug("Object already saved: {} -> {}".format(
                obj, self._cache.get_by_value(obj)))
            return self._cache.get_by_value(obj)
        else:
            saved_objects.add(obj)
            logger.debug("Saving: {} -> {}".format(
                obj, key or self._get_or_create_key(obj)))

        deflatable = self._adapt_to_IDeflatable(obj)
        blob = deflatable.deflate(self._get_or_create_key)
        if key is not None:
            blob.obj_key = key
        else:
            key = blob.obj_key

        # Send children out to storage
        blob.children = {self._save(None, c, saved_objects)
                         for c in blob.children}

        # Send parent out to storage
        self._cache[key] = obj
        self.store.set(key, blob)

        return key

    def load(self, key, reify=True):
        if key is None:
            return None
        if key in self._cache and reify:
            logger.info("Loading {} from cache".format(key))
            return self._cache[key]
        else:
            blob = self.store.get(key)

            if blob is None:
                raise ValueError("Key: {!r} unavailable".format(key))

            inflatable = self._adapt_to_IInflatable(blob)
            obj = inflatable.inflate(self.load, reify=reify)
            if reify:
                # Store in loaded object cache
                self._cache[key] = obj
            return obj

    def _adapt_to_IInflatable(self, blob):
        inflatable = self.adaptation_manager.adapt(
            blob, IInflatable, None)
        if inflatable is None:
            inflatable = DefaultInflator(blob)
        return inflatable

    def _adapt_to_IDeflatable(self, obj):
        # We use two different signatures because we want the "no adapter"
        # error message
        if self.use_default:
            deflatable = self.adaptation_manager.adapt(
                obj, IDeflatable, None)
            if not deflatable:
                deflatable = DefaultDeflator(obj)
        else:
            deflatable = self.adaptation_manager.adapt(
                obj, IDeflatable)
        return deflatable

    def _get_or_create_key(self, obj):
        return self._cache.setdefault(obj, uuid4())
