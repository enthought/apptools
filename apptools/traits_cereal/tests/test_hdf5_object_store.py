#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

# import json
# import uuid

from ..hdf5_object_store import HDF5ObjectStore
from .sample_data import TEST_ATTRS, Generic
from ..storage_manager import StorageManager


def test_roundtrip():
    # expected = Generic(**TEST_ATTRS)
    expected = Generic()

    sm = StorageManager(store=HDF5ObjectStore())
    expected_uuid = sm.save(expected)
    sm._cache_clear()

    result = sm.load(expected_uuid)
    assert result.get() == expected.get()


def test_very_nested_roundtrip():
    # We cannot put children in `set()`s for roundtrip tests because equality
    # testing on sets is by hash() which defaults to id()
    s0 = Generic(**TEST_ATTRS)
    s1 = Generic(**TEST_ATTRS)
    s1.dict_ = {'child_list': [s0, s0, s0]}


    expected = Generic(**TEST_ATTRS)
    expected.list_ = [{'24': {'Tron': (s0, None)}},
                      (s0, [s0, 98, s1], s1),
                      set([False])]

    sm = StorageManager(store=HDF5ObjectStore())
    expected_uuid = sm.save(expected)
    sm._cache_clear()

    result = sm.load(expected_uuid)
    assert result.get() == expected.get()

    rs0 = result.list_[0]['24']['Tron'][0]
    another_rs0 = result.list_[1][1][0]
    assert rs0 is another_rs0

    rs1 = result.list_[1][1][2]
    another_rs1 = result.list_[1][2]
    assert rs1 is another_rs1

    a_third_rs0 = rs1.dict_['child_list'][1]
    assert rs0 is a_third_rs0
