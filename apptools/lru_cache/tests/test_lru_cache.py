#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

from nose.tools import assert_equal

from ..lru_cache import LRUCache


def test_cache_callback():
    dropped = []
    callback = lambda *args: dropped.append(args)
    c = LRUCache(2, cache_drop_callback=callback)
    for i in range(5):
        c[i] = str(i)

    expected = [(0, '0'), (1, '1'), (2, '2')]
    assert_equal(expected, dropped)


def test_cache_len():
    c = LRUCache(2)
    assert_equal(0, len(c))
    assert_equal(2, c.size)
    c[0] = None
    assert_equal(1, len(c))
    assert_equal(2, c.size)
    c[1] = None
    assert_equal(2, len(c))
    assert_equal(2, c.size)
    c[2] = None
    assert_equal(2, len(c))
    assert_equal(2, c.size)


def test_cache_resize():
    c = LRUCache(1)
    c[0] = 0
    c[1] = 1

    assert_equal(1, len(c))
    assert_equal(1, c.size)
    assert 0 not in c
    assert 1 in c

    c.size = 3
    assert_equal(1, len(c))
    assert_equal(3, c.size)
    assert 1 in c

    c[2] = 2
    assert_equal(2, len(c))
    assert_equal(3, c.size)
    assert 1 in c
    assert 2 in c

    c[3] = 3
    assert_equal(3, len(c))
    assert_equal(3, c.size)
    assert 1 in c
    assert 2 in c
    assert 3 in c

    c[4] = 4
    assert_equal(3, len(c))
    assert_equal(3, c.size)
    assert 1 not in c
    assert 2 in c
    assert 3 in c
    assert 4 in c


def test_cache_items():
    c = LRUCache(2)
    assert_equal([], c.items())

    c[0] = str(0)
    c[1] = str(1)
    c[2] = str(2)

    expected = [(1, '1'), (2, '2')]
    assert_equal(expected, sorted(c.items()))


def test_cache_idempotency():
    c = LRUCache(2)
    c[1] = 1
    assert_equal(1, len(c))
    c[1] = 1
    assert_equal(1, len(c))

    c[2] = 2
    assert_equal(2, len(c))
    c[1] = 1
    assert_equal(2, len(c))
    c[2] = 2
    assert_equal(2, len(c))

    c[3] = 3
    assert_equal(2, len(c))
    c[3] = 3
    assert_equal(2, len(c))


def test_cache_keys_values():
    c = LRUCache(2)
    assert_equal([], c.items())

    c[0] = str(0)
    c[1] = str(1)
    c[2] = str(2)

    expected = [1, 2]
    assert_equal(expected, sorted(c.keys()))
    assert_equal([str(val) for val in expected], sorted(c.values()))


def test_cache_clear():
    c = LRUCache(2)
    for i in range(c.size):
        c[i] = i
    assert_equal(c.size, len(c))
    c.clear()
    assert_equal(0, len(c))


def test_cache_get():
    c = LRUCache(2)
    for i in range(c.size):
        c[i] = i
    assert_equal(0, c.get(0))
    assert_equal(None, c.get(c.size))


def test_updated_event():
    c = LRUCache(2)
    events = []

    # Traits can't handle builtins as handlers
    c.on_trait_change(lambda x: events.append(x), 'updated')

    c[0] = 0
    assert_equal(sorted(events), [[0]])

    c[1] = 1
    assert_equal(sorted(events), [[0], [0, 1]])

    c[2] = 2
    assert_equal(sorted(events), [[0], [0, 1], [1, 2]])

    # Getting items doesn't fire anything
    c[1]
    assert_equal(sorted(events), [[0], [0, 1], [1, 2]])

    c.get(3)
    assert_equal(sorted(events), [[0], [0, 1], [1, 2]])
