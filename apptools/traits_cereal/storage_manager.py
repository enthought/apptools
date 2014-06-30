#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

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


class StorageManager(HasStrictTraits):

    adaptation_manager = Instance(AdaptationManager)

    store = Supports(IObjectStore)

    use_default = Bool(True)

    _obj_to_uuid_cache = Instance(WeakKeyDictionary, WeakKeyDictionary)
    _uuid_to_obj_cache = Instance(WeakValueDictionary, WeakValueDictionary)

    def _adaptation_manager_default(self):
        return get_global_adaptation_manager()

    def _store_default(self):
        return HDF5ObjectStore()

    def save(self, obj):
        return self._save(obj, set())

    def _save(self, obj, saved_objects):
        if obj in saved_objects:
            logger.debug("Object already saved: {} -> {}".format(
                obj, self._obj_to_uuid_cache[obj]))
            return self._obj_to_uuid_cache[obj]
        else:
            saved_objects.add(obj)
            logger.debug("Saving: {} -> {}".format(
                obj, self._get_or_create_uuid(obj)))

        deflatable = self._adapt_to_IDeflatable(obj)
        blob = deflatable.deflate(self._get_or_create_uuid)
        key = blob.obj_uuid

        # Send children out to storage
        blob.children = {self._save(c, saved_objects) for c in blob.children}

        # Send parent out to storage
        self._cache_set(key, obj)
        self.store.set(key, blob)

        return key

    def load(self, key, reify=True):
        if self._cache_contains(key):
            logger.info("Loading {} from cache".format(key))
            return self._cache_get(key)
        else:
            blob = self.store.get(key)

            if blob is None:
                raise ValueError("Key: {!r} unavailable".format(key))

            inflatable = self._adapt_to_IInflatable(blob)
            obj = inflatable.inflate(self.load, reify=reify)
            if reify:
                # Store in loaded object cache
                self._cache_set(key, obj)
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

    def _get_or_create_uuid(self, obj):
        uuid = self._obj_to_uuid_cache.setdefault(obj, uuid4())
        self._uuid_to_obj_cache[uuid] = obj
        return uuid

    def _cache_contains(self, key):
        return key in self._obj_to_uuid_cache or key in self._uuid_to_obj_cache

    def _cache_set(self, key, val):
        self._uuid_to_obj_cache[key] = val
        self._obj_to_uuid_cache[val] = key

    def _cache_get(self, key):
        return self._uuid_to_obj_cache.get(key)

    def _cache_get_by_obj(self, obj):
        return self._obj_to_uuid_cache.get(obj)

    def _cache_del(self, key):
        val = self._uuid_to_obj_cache[key]
        del self._uuid_to_obj_cache[key]
        del self._obj_to_uuid_cache[val]

    def _cache_clear(self):
        """ DANGER!!! Clear everything out of this StorageManager's cache.

        This is mainly for testing purposes, but can be useful to force
        reloading objects from disk.
        """
        self._obj_to_uuid_cache.clear()
        self._uuid_to_obj_cache.clear()
