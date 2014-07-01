#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

from uuid import uuid4
import mock

from numpy.testing import assert_raises
from traits.api import AdaptationError

from ..interfaces import IObjectStore
from .sample_data import Generic, TEST_ATTRS
from ..storage_manager import StorageManager


def exploding_object_store():
    msg = "StorageManager.store.{} called"
    m = mock.MagicMock(IObjectStore)
    m.get.side_effect = AssertionError(msg.format('get'))
    m.set.side_effect = AssertionError(msg.format('set'))
    return m


def test_disabling_default_adapter_fails_without_adapter():
    sm = StorageManager()

    # Without it we fail
    sm.use_default = False
    assert_raises(AdaptationError, sm.save, Generic())

    # With it we succeed
    sm.use_default = True
    sm.save(Generic())


def test_save_then_load_returns_same_instance():
    sm = StorageManager()
    expected = Generic(**TEST_ATTRS)
    result = sm.load(sm.save(expected))
    assert result is expected


def test_load_hits_cache_first():
    sm = StorageManager(store=exploding_object_store())
    expected = Generic()
    key = uuid4()

    sm._cache[key] = expected
    result = sm.load(key)

    assert result is expected


def test_cache_allows_gc():
    sm = StorageManager()

    expected = Generic()

    sm.save(expected)


def test_load_twice_returns_same_instance():
    sm = StorageManager()
    expected = Generic(**TEST_ATTRS)
    key = sm.save(expected)

    # With caching
    obj00 = sm.load(key)
    obj01 = sm.load(key)

    # Without caching
    sm._cache.clear()
    obj10 = sm.load(key)
    obj11 = sm.load(key)

    assert obj00 is obj01
    assert obj10 is obj11
    assert obj00 is not obj10
    assert obj01 is not obj11


def test_save_updates_load_cache():
    sm = StorageManager()
    expected = Generic(**TEST_ATTRS)
    key = sm.save(expected)

    # With caching
    obj00 = sm.load(key)
    obj01 = sm.load(key)

    # Without caching
    sm._cache.clear()
    obj10 = sm.load(key)
    obj11 = sm.load(key)

    assert obj00 is obj01
    assert obj10 is obj11
    assert obj00 is not obj10
    assert obj01 is not obj11


def test_calls_to_save_are_idempotent():
    sm = StorageManager()
    parent = Generic(child_=Generic())

    parent_key = sm.save(parent)
    child_key = sm.save(parent.child_)

    parent_blob = sm.load(parent_key, reify=False)

    assert child_key == parent_blob.obj_attrs['child_'].obj_uuid
