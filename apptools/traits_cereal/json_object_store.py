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

#FIXME: We should try very hard here to replace a lot of this with JSONPickle

SPECIAL_KEY = u'__SPECIAL__'


@provides(IObjectStore)
class JSONObjectStore(HasTraits):

    """ An IObjectStore backed by a JSON file. """

    #: The filename of the JSON storage on disk
    filename = File(os.path.join(tempfile.gettempdir(), 'object_store.json'))

    #: A Callable that turns values into JSON
    _encode = Callable

    #: A Callable that turns JSON into values
    _decode = Callable

    #: A python representation of the JSON file
    _disk_mirror = Dict

    ### Traits defaults #######################################################

    def __encode_default(self):
        return JSONBlobEncoder(indent=4, sort_keys=True).encode

    def __decode_default(self):
        return JSONBlobDecoder().decode

    ### IObjectStore interface ################################################

    def set(self, key, value):
        """ Associate the `value` with `key` and update the JSON file. """
        key = self._normalize_key(key)
        self._disk_mirror[key] = value
        with open(self.filename, 'w') as fp:
            fp.write(self._encode(self._disk_mirror))
        return

    def get(self, key):
        """ Retrieve the value associated with the `key`. """
        key = self._normalize_key(key)
        with open(self.filename, 'r') as fp:
            data = fp.read()
        self._disk_mirror = self._decode(data)
        return self._disk_mirror[key]

    ### Private methods #######################################################

    def _normalize_key(self, key):
        """ Ensure that `key` is formatted correctly for JSON files. """
        if isinstance(key, UUID):
            key = key.urn
        return key


class JSONBlobEncoder(json.JSONEncoder):

    """ A JSONEncoder that knows how to encode UUID's and Blobs. """

    def encode(self, obj):
        """ Encode `obj` as a JSON string. """
        # We need to intercept the json modules' inability to
        # roundtrip native types like tuple
        return super(JSONBlobEncoder, self).encode(self._convert(obj))

    def default(self, obj):
        """ Called when JSONEncoder doesn't know what to do, attempt to return
        a non-standard object in a JSON-able format. """
        ret = self._convert(obj)
        if ret is not obj:
            return ret
        else:
            # This raises JSONEncoder's failure exception
            super(JSONBlobEncoder, self).default(obj)

    ### Private methods #######################################################

    def _convert(self, obj):
        """ Convert an object to a representation suitable for JSON. """
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

    def _make_object(self, typename, obj):
        """ Render a typename and corresponding object as JSON. """
        return {SPECIAL_KEY: (typename, obj)}


class JSONBlobDecoder(json.JSONDecoder):

    """ A JSONDecoder that knows how to decode JSON written by
    `JSONBlobEncoder`. """

    def __init__(self, **kwargs):
        args = ('utf-8', _decoder_object_hook)
        super(JSONBlobDecoder, self).__init__(*args, **kwargs)


def _decoder_object_hook(obj):
    """ Return the python object represented by the dict `obj`.

    This is used by json.JSONDecoder when deserializing.
    """
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
