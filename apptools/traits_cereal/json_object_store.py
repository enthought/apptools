#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import tempfile
from uuid import UUID

from traits.api import Callable, Dict, File, HasTraits, provides

from .blob import Blob
from .interfaces import IObjectStore
from .utils import get_obj_of_type

SPECIAL_KEY = u'__SPECIAL__'


def decoder_object_hook(obj):
    hooks = {'UUID': UUID,
             'set': set,
             'tuple': tuple,
             'Blob': lambda val: Blob(**val)}
    key = obj.get(SPECIAL_KEY)
    if key is not None:
        name, val = key
        if name in hooks:
            return hooks[name](val)
    return obj


@provides(IObjectStore)
class JSONObjectStore(HasTraits):

    """ An IObjectStore backed by a JSON file. """

    #: The filename of the JSON storage on disk
    filename = File(os.path.join(tempfile.gettempdir(), 'object_store.json'))

    #: The function for turning values into JSON
    _encode = Callable

    #: The function for turning JSON into values
    _decode = Callable

    #: A python representation of the JSON file
    _disk_mirror = Dict

    def __encode_default(self):
        return JSONBlobEncoder(indent=4, sort_keys=True).encode

    def __decode_default(self):
        return JSONBlobDecoder().decode

    def set(self, key, val):
        key = self._normalize_key(key)
        self._disk_mirror[key] = val
        with open(self.filename, 'w') as fp:
            fp.write(self._encode(self._disk_mirror))
        return

    def get(self, key):
        key = self._normalize_key(key)
        with open(self.filename, 'r') as fp:
            data = fp.read()
        self._disk_mirror = self._decode(data)
        return self._disk_mirror[key]

    def _normalize_key(self, key):
        if isinstance(key, UUID):
            key = key.urn
        return key


class JSONBlobEncoder(json.JSONEncoder):

    def _make_object(self, typename, obj):
        return {SPECIAL_KEY: (typename, obj)}

    def default(self, obj):
        ret = self._convert(obj)
        if ret is not obj:
            return ret
        else:
            super(JSONBlobEncoder, self).default(obj)

    def _convert(self, obj):
        obj = get_obj_of_type(obj)
        if isinstance(obj, dict):
            assert all(isinstance(key, basestring) for key in obj)  # noqa
            return {k: self._convert(v) for k, v in obj.items()}
        if isinstance(obj, UUID):
            return self._make_object('UUID', obj.urn)
        if isinstance(obj, set):
            return self._make_object('set', map(self._convert, obj))
        if isinstance(obj, tuple):
            return self._make_object('tuple', map(self._convert, obj))
        if isinstance(obj, list):
            return map(self._convert, obj)
        if isinstance(obj, Blob):
            attrs = obj.__getstate__()
            attrs.pop('__traits_version__')
            return self._make_object('Blob', self._convert(attrs))
        return obj

    def encode(self, obj):
        # We need to intercept the json modules' inability to
        # roundtrip native types like tuple
        return super(JSONBlobEncoder, self).encode(self._convert(obj))


class JSONBlobDecoder(json.JSONDecoder):

    def __init__(self, **kwargs):
        args = ('utf-8', decoder_object_hook)
        super(JSONBlobDecoder, self).__init__(*args, **kwargs)
