#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import json
import uuid

from ..blob import Blob
from ..json_object_store import (
    JSONBlobDecoder, JSONBlobEncoder, JSONObjectStore, SPECIAL_KEY)
from .sample_data import TEST_ATTRS, Generic
from ..storage_manager import StorageManager


BE = JSONBlobEncoder()
BD = JSONBlobDecoder()


def encode(typename, obj):
    return json.dumps({SPECIAL_KEY: (typename, obj)})


def test_encode_set():
    result = BE.encode(set([1, 2, 3]))
    expected = encode('set', [1, 2, 3])
    assert result == expected


def test_encode_uuid():
    u = uuid.uuid4()
    result = BE.encode(u)
    expected = encode('UUID', u.urn)
    assert result == expected


def test_encode_blob():
    b = Blob()
    result = json.loads(BE.encode(b))
    expected = json.loads(
        encode('Blob', {'obj_attrs': {},
                        'children': json.loads(encode('set', [])),
                        'class_name': '',
                        'obj_key': None,
                        'version': 0}))
    assert result == expected


def test_decode_set():
    result = BD.decode('{"__SPECIAL__": ["set", [1, 2, 3]]}')
    expected = set([1, 2, 3])
    assert result == expected


def test_decode_uuid():
    u = uuid.uuid4()
    result = BD.decode('{"__SPECIAL__": ["UUID", "' + u.urn + '"]}')
    expected = u
    assert result == expected


def test_decode_blob():
    u = uuid.uuid4()
    data = '''{"__SPECIAL__": ["Blob", {
        "obj_attrs": {},
        "children": {"__SPECIAL__": ["set", []]},
        "class_name": "",
        "obj_key": {"__SPECIAL__": ["UUID", "''' + u.urn + '''"]},
        "version": 0
    }]}'''
    result = BD.decode(data)
    expected = Blob()
    expected.obj_key = u
    assert result.get() == expected.get()


def test_roundtrip():
    expected = Generic(**TEST_ATTRS)
    sm = StorageManager(store=JSONObjectStore())
    expected_key = sm.save(expected)
    sm._cache.clear()

    result = sm.load(expected_key)
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

    sm = StorageManager(store=JSONObjectStore())
    expected_key = sm.save(expected)
    sm._cache.clear()

    result = sm.load(expected_key)
    assert result.get() == expected.get()

    rs0 = result.list_[0]['24']['Tron'][0]
    another_rs0 = result.list_[1][1][0]
    assert rs0 is another_rs0

    rs1 = result.list_[1][1][2]
    another_rs1 = result.list_[1][2]
    assert rs1 is another_rs1

    a_third_rs0 = rs1.dict_['child_list'][1]
    assert rs0 is a_third_rs0
