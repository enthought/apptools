#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import uuid

from ..blob import Blob
from ..yaml_object_store import YAMLObjectStore
from .sample_data import TEST_ATTRS, Generic
from ..storage_manager import StorageManager

YOS = YAMLObjectStore()


def yaml_str(s):
    return s


def yaml_empty_blob(uuid):
    return (
        "!traits_cereal/Blob\n"
        "children: !!set {{}}\n"
        "class_name: ''\n"
        "obj_attrs: {{}}\n"
        "obj_uuid: {0}\n"
        "version: 0\n").format(uuid or 'null')


def test_encode_uuid():
    u = uuid.uuid4()
    result = YOS._encode(u)
    expected = yaml_str(u.urn)
    assert result == expected


def test_decode_uuid():
    expected = uuid.uuid4()
    result = YOS._decode(yaml_str(expected.urn))
    assert result == expected


def test_encode_blob():
    b = Blob()
    result = YOS._encode(b)
    expected = yaml_empty_blob(b.obj_uuid)
    assert result == expected


def test_roundtrip():
    expected = Generic(**TEST_ATTRS)
    sm = StorageManager(store=YAMLObjectStore())
    expected_uuid = sm.save(expected)
    sm._cache.clear()

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

    sm = StorageManager(store=YAMLObjectStore())
    expected_uuid = sm.save(expected)
    sm._cache.clear()

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
