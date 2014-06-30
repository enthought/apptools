#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

from uuid import uuid4

from .assertions import assert_container_has_no_HasTraits
from ..blob import blob_skeleton
from ..default_storage_adapters import DefaultInflator, DefaultDeflator
from .sample_data import TEST_ATTRS, Generic

import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8.8s [%(name)s:%(lineno)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level='INFO')
logger = logging.getLogger(__name__)


def test_blob(uuid=None):
    blob = blob_skeleton(
        Generic(),
        uuid_factory=(lambda x: uuid) if uuid else None,
        obj_attrs=dict(TEST_ATTRS))
    return blob


def inflator_callback_factory(objs, get_or_create_uuid):
    return {get_or_create_uuid(o): o for o in objs}.get


def get_or_create_uuid_factory():
    d = {}

    def get_or_create_uuid(obj):
        return d.setdefault(obj, uuid4())

    return get_or_create_uuid


def test_deflate_simple():
    s = Generic(**TEST_ATTRS)
    result = DefaultDeflator(s).deflate(get_or_create_uuid_factory())
    expected = test_blob(result.obj_uuid)
    compare_blobs(result, expected)


def test_inflate_simple():
    blob = test_blob()
    obj_uuid = blob.obj_uuid
    result = DefaultInflator(blob).inflate(lambda: None, reify=False)
    expected = test_blob(obj_uuid)
    compare_blobs(result, expected)


def test_deflate_child_attr():
    get_or_create_uuid = get_or_create_uuid_factory()
    s0 = Generic()
    s1 = Generic(child_=s0)

    result = DefaultDeflator(s1).deflate(get_or_create_uuid)

    expected = test_blob(result.obj_uuid)
    expected.obj_attrs = {'child_': get_or_create_uuid(s0)}
    expected.children = set([s0])

    compare_blobs(result, expected)


def test_inflate_child_attr():
    get_or_create_uuid = get_or_create_uuid_factory()
    s0 = Generic()

    blob1 = test_blob()
    blob1.obj_attrs = {'child_': get_or_create_uuid(s0)}
    blob1.children = set([s0])

    cb = inflator_callback_factory(blob1.children, get_or_create_uuid)

    result = DefaultInflator(blob1).inflate(cb, reify=False)

    expected = test_blob(blob1.obj_uuid)
    expected.obj_attrs = {'child_': s0}
    expected.children = set([s0])

    compare_blobs(result, expected)


def test_deflate_child_in_list():
    get_or_create_uuid = get_or_create_uuid_factory()
    s0 = Generic()
    s1 = Generic(list_=[s0])

    result = DefaultDeflator(s1).deflate(get_or_create_uuid)

    expected = test_blob(get_or_create_uuid(s1))
    expected.obj_attrs = {'list_': [get_or_create_uuid(s0)]}
    expected.children = set([s0])

    assert_container_has_no_HasTraits(result.obj_attrs)
    compare_blobs(result, expected)


def test_inflate_child_in_list():
    get_or_create_uuid = get_or_create_uuid_factory()
    s0 = Generic()

    blob1 = test_blob()
    blob1.obj_attrs = {'list_': [get_or_create_uuid(s0)]}
    blob1.children = set([s0])

    cb = inflator_callback_factory([s0], get_or_create_uuid)

    result = DefaultInflator(blob1).inflate(cb, reify=False)

    expected = test_blob(blob1.obj_uuid)
    expected.obj_attrs = {'list_': [s0]}
    expected.children = set([s0])

    compare_blobs(result, expected)


def test_deflate_child_in_tuple():
    get_or_create_uuid = get_or_create_uuid_factory()
    s0 = Generic()
    s1 = Generic(tuple_=(s0,))

    result = DefaultDeflator(s1).deflate(get_or_create_uuid)

    expected = test_blob(result.obj_uuid)
    expected.obj_attrs = {'tuple_': (get_or_create_uuid(s0),)}
    expected.children = set([s0])

    assert_container_has_no_HasTraits(result.obj_attrs)
    compare_blobs(result, expected)


def test_inflate_child_in_tuple():
    get_or_create_uuid = get_or_create_uuid_factory()
    s0 = Generic()

    blob1 = test_blob()
    blob1.obj_attrs = {'tuple_': (get_or_create_uuid(s0),)}
    blob1.children = set([s0])

    cb = inflator_callback_factory([s0], get_or_create_uuid)

    result = DefaultInflator(blob1).inflate(cb, reify=False)

    expected = test_blob(blob1.obj_uuid)
    expected.obj_attrs = {'tuple_': (s0,)}
    expected.children = set([s0])

    compare_blobs(result, expected)


def test_deflate_child_in_set():
    get_or_create_uuid = get_or_create_uuid_factory()
    s0 = Generic()
    s1 = Generic(set_=set([s0]))

    result = DefaultDeflator(s1).deflate(get_or_create_uuid)

    expected = test_blob(result.obj_uuid)
    expected.obj_attrs = {'set_': set([get_or_create_uuid(s0)])}
    expected.children = set([s0])

    assert_container_has_no_HasTraits(result.obj_attrs)
    compare_blobs(result, expected)


def test_inflate_child_in_set():
    get_or_create_uuid = get_or_create_uuid_factory()
    s0 = Generic()

    blob1 = test_blob()
    blob1.obj_attrs = {'set_': set([get_or_create_uuid(s0)])}
    blob1.children = set([s0])

    cb = inflator_callback_factory([s0], get_or_create_uuid)

    result = DefaultInflator(blob1).inflate(cb, reify=False)

    expected = test_blob(result.obj_uuid)
    expected.obj_attrs = {'set_': set([s0])}
    expected.children = set([s0])

    compare_blobs(result, expected)


def test_deflate_children_in_dict():
    get_or_create_uuid = get_or_create_uuid_factory()
    s0 = Generic()
    s1 = Generic()
    s2 = Generic(dict_={"child_as_value": s0,
                        s1: "child_as_key"})

    result = DefaultDeflator(s2).deflate(get_or_create_uuid)

    expected = test_blob(result.obj_uuid)
    expected.obj_attrs = {'dict_': {"child_as_value": get_or_create_uuid(s0),
                                    get_or_create_uuid(s1): "child_as_key"}}
    expected.children = set([s0, s1])

    assert_container_has_no_HasTraits(result.obj_attrs)
    compare_blobs(result, expected)


def test_inflate_children_in_dict():
    get_or_create_uuid = get_or_create_uuid_factory()
    s0 = Generic()
    s1 = Generic()
    blob2 = test_blob()
    blob2.obj_attrs = {'dict_': {"child_as_value": get_or_create_uuid(s0),
                                 get_or_create_uuid(s1): "child_as_key"}}
    blob2.children = set([s0, s1])

    cb = inflator_callback_factory([s0, s1], get_or_create_uuid)

    result = DefaultInflator(blob2).inflate(cb, reify=False)

    expected = test_blob(result.obj_uuid)
    expected.obj_attrs = {'dict_': {"child_as_value": s0,
                                    s1: "child_as_key"}}
    expected.children = set([s0, s1])

    compare_blobs(result, expected)


def test_deflate_nested_children():
    get_or_create_uuid = get_or_create_uuid_factory()
    s0 = Generic()
    s1 = Generic(dict_={'child_list': [s0, s0, s0]})
    blob2 = test_blob()
    blob2.obj_attrs = {'list_': [(get_or_create_uuid(s1),)]}
    blob2.children = set([s1])

    cb = inflator_callback_factory([s1], get_or_create_uuid)

    result = DefaultInflator(blob2).inflate(cb, reify=False)

    expected = test_blob(result.obj_uuid)
    expected.obj_attrs = {'list_': [(s1,)]}
    expected.children = set([s1])

    compare_blobs(result, expected)


def test_inflate_nested_children():
    get_or_create_uuid = get_or_create_uuid_factory()
    s0 = Generic()
    s1 = Generic(dict_={'child_list': [s0, s0, s0]})
    blob2 = test_blob()
    blob2.obj_attrs = {'list_': [(get_or_create_uuid(s1),)]}
    blob2.children = set([s1])

    cb = inflator_callback_factory([s1], get_or_create_uuid)

    result = DefaultInflator(blob2).inflate(cb, reify=False)

    expected = test_blob(result.obj_uuid)
    expected.obj_attrs = {'list_': [(s1,)]}
    expected.children = set([s1])

    compare_blobs(result, expected)


def test_deflate_very_nested_children():
    get_or_create_uuid = get_or_create_uuid_factory()
    s0 = Generic()
    s1 = Generic(dict_={'child_list': [s0, s0, s0]})
    s2 = Generic(list_=[{s0: {s1: s0}},
                        (s0, [s0, s1], s1),
                        set([(s0,)])])

    result = DefaultDeflator(s2).deflate(get_or_create_uuid)

    s0_uuid = get_or_create_uuid(s0)
    s1_uuid = get_or_create_uuid(s1)

    expected = test_blob(get_or_create_uuid(s2))
    expected.obj_attrs = {'list_': [{s0_uuid: {s1_uuid: s0_uuid}},
                                    (s0_uuid, [s0_uuid, s1_uuid], s1_uuid),
                                    set([(s0_uuid,)])]}
    expected.children = set([s0, s1])

    assert_container_has_no_HasTraits(result.obj_attrs)
    compare_blobs(result, expected)


def test_inflate_very_nested_children():
    get_or_create_uuid = get_or_create_uuid_factory()
    s0 = Generic()
    s1 = Generic(dict_={'child_list': [s0, s0, s0]})
    blob2 = test_blob()

    s0_uuid = get_or_create_uuid(s0)
    s1_uuid = get_or_create_uuid(s1)

    blob2.obj_attrs = {'list_': [{s0_uuid: {s1_uuid: s0_uuid}},
                                 (s0_uuid, [s0_uuid, s1_uuid], s1_uuid),
                                 set([(s0_uuid,)])]}
    blob2.children = set([s0, s1])

    cb = inflator_callback_factory([s0, s1], get_or_create_uuid)

    result = DefaultInflator(blob2).inflate(cb, reify=False)

    expected = test_blob(blob2.obj_uuid)
    expected.obj_attrs = {'list_': [{s0: {s1: s0}},
                                    (s0, [s0, s1], s1),
                                    set([(s0,)])]}
    expected.children = set([s0, s1])

    compare_blobs(result, expected)


def compare_blobs(result_blob, expected_blob):
    assert result_blob.get() == expected_blob.get()
