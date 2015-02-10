# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# Copyright (c) 2015, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# The circular buffer implementation was backported from Python 3.4 and is
# provided under the PSF License available at
# https://docs.python.org/3.4/license.html
#
# Author: Enthought, Inc.
#------------------------------------------------------------------------------


from threading import RLock
from collections import OrderedDict
import logging

from traits.api import Callable, Event, HasStrictTraits, Instance, Int

logger = logging.getLogger(__name__)


class LRUCache(HasStrictTraits):
    """ A least-recently used cache.

    Items older than `size()` accesses are dropped from the cache.

    This is ported from python 3's functools.lru_cache.

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

    def _initialize_cache(self, force=False):
        with self._lock:
            if self._cache is None:
                self._cache = OrderedDict()
            else:
                self._cache.clear()

    def _renew(self, key):
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
            self._cache[key] = result
            self._renew(key)
            if self.size < len(self._cache):
                dropped = self._cache.popitem(last=False)
                if self.cache_drop_callback is not None:
                    self.cache_drop_callback(*dropped)
        finally:
            self.updated = self.keys()

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def items(self):
        return self._cache.items()

    def keys(self):
        return self._cache.keys()

    def values(self):
        return self._cache.values()

    def clear(self):
        self._initialize_cache()
        self.updated = []
