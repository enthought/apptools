#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import collections
import contextlib
import os
import tempfile
from uuid import UUID

from apptools.io.h5.file import H5File
from traits.api import Callable, File, HasTraits, Instance, provides

from .blob import Blob
from .interfaces import IObjectStore
from .utils import class_qualname
from .yaml_object_store import yaml_encoder_factory, yaml_decoder_factory


PROTOCOL_TAG = "__PROTOCOL__"
VERSION_TAG = "__VERSION__"


@provides(IObjectStore)
class HDF5ObjectStore(HasTraits):

    """An IObjectStore that is backed by an HDF5 file. """

    #: A Callable that turns values into YAML
    _encode = Callable

    #: A Callable that turns YAML into values
    _decode = Callable

    #: The H5File that is currently open
    _file = Instance(H5File)

    #: The filename of the YAML storage on disk
    filename = File(os.path.join(tempfile.gettempdir(), 'object_store.h5'))

    ### Traits defaults #######################################################

    def __encode_default(self):
        return yaml_encoder_factory(default_flow_style=True, width=int(1e4))

    def __decode_default(self):
        return yaml_decoder_factory()

    ### IObjectStore interface ################################################

    def set(self, key, val):
        """ Store the `value` under the path `key`, opening and closing the
        H5File. """
        with self._open():
            return self._set(key, val)

    def get(self, key):
        """ Return the value stored under the path `key`, opening and closing
        the H5File. """
        with self._open():
            return self._get(key)

    ### Private methods #######################################################

    def _get(self, key):
        """ Return the value stored under path `key`, potentially recursing to
        retrieve children.

        The H5File is assumed to be open.
        """
        key = self._normalize_key(key)
        group = self._file[key]

        group_attrs = dict(group.attrs.items())
        obj_attrs = {}

        # Check special attributes
        class_path = group_attrs.pop(PROTOCOL_TAG, '__builtin__.dict')
        group_attrs.pop(VERSION_TAG, 1)

        for attr, val in group_attrs.items():
            if isinstance(val, basestring):
                try:
                    # We encoded the value on the way in, let's decode it.
                    val = self._decode(val)
                except ValueError as e:
                    raise ValueError("{} from {!r}".format(e, val))
            obj_attrs[attr] = val

        #
        for subgroup in group.subgroup_names:
            subgroup_path = self._file.join_path(key, subgroup)
            obj_attrs[subgroup] = self._get(subgroup_path)

        # Turn special groups back into the object they represented
        modpath, clsname = class_path.rsplit('.', 1)
        mod = __import__(modpath, fromlist=[clsname])
        klass = getattr(mod, clsname)
        obj = klass(**obj_attrs)

        return obj

    def _normalize_key(self, key):
        """ Ensure that `key` is formatted correctly for HDF5 files and
        prepended with "/objects". """
        if isinstance(key, UUID):
            # UUID.urn contains ':' which makes pytables raise a warning
            key = "UUID__" + key.hex
        if '/' in key:
            path, node = self._file.split_path(key)
        else:
            path, node = '', key
        if not path.startswith('/objects'):
            path = self._file.join_path('objects', path)
        path = self._file.join_path(path, node)
        return path

    @contextlib.contextmanager
    def _open(self):
        """ Open and yield our H5File. Close it when the context ends. """
        try:
            fn = H5File(filename=self.filename,
                        mode='a',
                        delete_existing=True,
                        auto_groups=True,
                        chunked=False)
            self._file = fn
            with contextlib.closing(fn):
                yield
        finally:
            self._file = None

    def _set(self, key, value):
        """ Store the `value` under path `key`.

        The H5File is assumed to be open.
        """
        key = self._normalize_key(key)

        if not isinstance(value, Blob):
            raise TypeError("All Blobs, all the time.")

        #FIXME: add this to H5File api for creating groups, perhaps?
        group = self._file._check_node(key)

        #FIXME: H5File should just return the group here
        self._file.create_group(key)
        group = self._file[key]

        value_attrs = value.__getstate__()
        value_attrs.pop('__traits_version__')

        group.attrs[PROTOCOL_TAG] = class_qualname(value)
        group.attrs[VERSION_TAG] = 1

        for attr, val in value_attrs.items():
            self._store_obj_in_group(group, attr, val)

    def _store_obj_in_group(self, group, key, val):
        """ Store the `value` under attribute `key` on the `group`.
        If `value` is a `Mapping`, create a subgroup and recurse. """
        if isinstance(val, collections.Mapping):
            mapping = val
            path = group._h5_group._v_pathname
            path = self._file.join_path(path, key)
            self._file.create_group(path)
            subgroup = self._file[path]
            subgroup.attrs[PROTOCOL_TAG] = class_qualname(mapping)
            subgroup.attrs[VERSION_TAG] = 1
            for k, v in mapping.items():
                self._store_obj_in_group(subgroup, k, v)
        else:
            # Store encoded values as strings to avoid pickle.
            group.attrs[key] = self._encode(val)
