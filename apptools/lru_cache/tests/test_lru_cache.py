#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

import unittest

from ..lru_cache import LRUCache


class LRUCacheTestCase(unittest.TestCase):
    def test_cache_callback(self):
        dropped = []
        callback = lambda *args: dropped.append(args)
        c = LRUCache(2, cache_drop_callback=callback)
        for i in range(5):
            c[i] = str(i)

        expected = [(0, '0'), (1, '1'), (2, '2')]
        self.assertEqual(expected, dropped)

    def test_cache_len(self):
        c = LRUCache(2)
        self.assertEqual(0, len(c))
        self.assertEqual(2, c.size)
        c[0] = None
        self.assertEqual(1, len(c))
        self.assertEqual(2, c.size)
        c[1] = None
        self.assertEqual(2, len(c))
        self.assertEqual(2, c.size)
        c[2] = None
        self.assertEqual(2, len(c))
        self.assertEqual(2, c.size)

    def test_cache_resize(self):
        c = LRUCache(1)
        c[0] = 0
        c[1] = 1

        self.assertEqual(1, len(c))
        self.assertEqual(1, c.size)
        assert 0 not in c
        assert 1 in c

        c.size = 3
        self.assertEqual(1, len(c))
        self.assertEqual(3, c.size)
        assert 1 in c

        c[2] = 2
        self.assertEqual(2, len(c))
        self.assertEqual(3, c.size)
        assert 1 in c
        assert 2 in c

        c[3] = 3
        self.assertEqual(3, len(c))
        self.assertEqual(3, c.size)
        assert 1 in c
        assert 2 in c
        assert 3 in c

        c[4] = 4
        self.assertEqual(3, len(c))
        self.assertEqual(3, c.size)
        assert 1 not in c
        assert 2 in c
        assert 3 in c
        assert 4 in c

    def test_cache_items(self):
        c = LRUCache(2)
        self.assertEqual([], c.items())

        c[0] = str(0)
        c[1] = str(1)
        c[2] = str(2)

        expected = [(1, '1'), (2, '2')]
        self.assertEqual(expected, sorted(c.items()))

    def test_cache_idempotency(self):
        c = LRUCache(2)
        c[1] = 1
        self.assertEqual(1, len(c))
        c[1] = 1
        self.assertEqual(1, len(c))

        c[2] = 2
        self.assertEqual(2, len(c))
        c[1] = 1
        self.assertEqual(2, len(c))
        c[2] = 2
        self.assertEqual(2, len(c))

        c[3] = 3
        self.assertEqual(2, len(c))
        c[3] = 3
        self.assertEqual(2, len(c))

    def test_cache_keys_values(self):
        c = LRUCache(2)
        self.assertEqual([], c.items())

        c[0] = str(0)
        c[1] = str(1)
        c[2] = str(2)

        expected = [1, 2]
        self.assertEqual(expected, sorted(c.keys()))
        self.assertEqual([str(val) for val in expected], sorted(c.values()))

    def test_cache_clear(self):
        c = LRUCache(2)
        for i in range(c.size):
            c[i] = i
        self.assertEqual(c.size, len(c))
        c.clear()
        self.assertEqual(0, len(c))

    def test_cache_get(self):
        c = LRUCache(2)
        for i in range(c.size):
            c[i] = i
        self.assertEqual(0, c.get(0))
        self.assertEqual(None, c.get(c.size))

    def test_updated_event(self):
        c = LRUCache(2)
        events = []

        # Traits can't handle builtins as handlers
        c.on_trait_change(lambda x: events.append(x), 'updated')

        c[0] = 0
        self.assertEqual(sorted(events), [[0]])

        c[1] = 1
        self.assertEqual(sorted(events), [[0], [0, 1]])

        c[2] = 2
        self.assertEqual(sorted(events), [[0], [0, 1], [1, 2]])

        # Getting items doesn't fire anything
        c[1]
        self.assertEqual(sorted(events), [[0], [0, 1], [1, 2]])

        c.get(3)
        self.assertEqual(sorted(events), [[0], [0, 1], [1, 2]])
