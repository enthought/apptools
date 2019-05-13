# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# Copyright (c) 2015, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Enthought, Inc.
# -----------------------------------------------------------------------------

from threading import RLock

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


from traits.api import Callable, Event, HasStrictTraits, Instance, Int


class LRUCache(HasStrictTraits):
    """ A least-recently used cache.

    Items older than `size()` accesses are dropped from the cache.

    """

    size = Int

    # Called with the key and value that was dropped from the cache
    cache_drop_callback = Callable

    # This event contains the set of cached cell keys whenever it changes
    updated = Event()

    _lock = Instance(RLock, args=())

    _cache = Instance(OrderedDict)

    def __init__(self, size, **traits):
        self.size = size
        self._initialize_cache()
        super(LRUCache, self).__init__(**traits)

    def _initialize_cache(self):
        with self._lock:
            if self._cache is None:
                self._cache = OrderedDict()
            else:
                self._cache.clear()

    def _renew(self, key):
        with self._lock:
            r = self._cache.pop(key)
            self._cache[key] = r
        return r

    # -------------------------------------------------------------------------
    # LRUCache interface
    # -------------------------------------------------------------------------

    def __contains__(self, key):
        with self._lock:
            return key in self._cache

    def __len__(self):
        with self._lock:
            return len(self._cache)

    def __getitem__(self, key):
        with self._lock:
            return self._renew(key)

    def __setitem__(self, key, result):
        try:
            dropped = None
            with self._lock:
                self._cache[key] = result
                self._renew(key)
                if self.size < len(self._cache):
                    dropped = self._cache.popitem(last=False)
            if dropped and self.cache_drop_callback is not None:
                self.cache_drop_callback(*dropped)
        finally:
            self.updated = list(self.keys())

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def items(self):
        with self._lock:
            return list(self._cache.items())

    def keys(self):
        with self._lock:
            return list(self._cache.keys())

    def values(self):
        with self._lock:
            return list(self._cache.values())

    def clear(self):
        with self._lock:
            self._initialize_cache()
        self.updated = []
