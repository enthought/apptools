#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import os
import re
import tempfile
import yaml
from functools import partial
from uuid import UUID

from traits.api import Callable, Dict, File, HasTraits, provides
from traits.trait_handlers import (
    TraitDictObject, TraitListObject, TraitSetObject)

from .blob import Blob
from .interfaces import IObjectStore

# Magic keys representing special classes that we care about
YAML_TAG_BLOB = u'!traits_cereal/Blob'
YAML_TAG_UUID = u'!UUID'

# This regex matches uuid.UUID.hex and uuid.UUID.urn formatted strings,
# allowing the YAML to avoid using YAML_TAG_UUID explicitly
UUID_REGEX = pattern = re.compile(
    '^(?:urn:uuid:)?'  # Optional prefix
    '(?:[0-9a-f]{8}'  # 8 hex
    '(?:-[0-9a-f]{4}){3}'  # (hyphen 4 hex) 3 times
    '-[0-9a-f]{12}'  # hyphen 12 hex
    '|[0-9a-f]{32})')  # or just 32 hex, no hyphens


# Functions for representing special classes as YAML
def _represent_uuid(dumper, data):
    """ Represent a UUID as YAML. """
    return dumper.represent_scalar(YAML_TAG_UUID, data.urn)


def _represent_blob(dumper, blob):
    """ Represent a Blob as YAML. """
    node = dumper.represent_object(blob)
    node.tag = YAML_TAG_BLOB
    # Throw away the __traits_version__ that comes from Blob.__getstate__()
    node.value = [v for v in node.value
                  if v[0].value != u'__traits_version__']
    return node


# Functions for constructing special classes from YAML
def _construct_uuid(loader, node):
    """ Instantiate a UUID from YAML. """
    value = loader.construct_scalar(node)
    return UUID(value)


def _construct_blob(loader, node):
    """ Instantiate a Blob from YAML. """
    blob_attrs = loader.construct_mapping(node, deep=True)
    blob = Blob(**blob_attrs)
    return blob


def yaml_encoder_factory(**kwargs):
    """ Return a callable that encodes its arguments as YAML. """
    suffix = '\n...\n'
    suffix_slice = slice(-len(suffix))

    factory_kwargs = dict(Dumper=dumper_factory)
    factory_kwargs.update(kwargs)

    def dump(*args, **kwargs):

        final_kwargs = factory_kwargs.copy()
        final_kwargs.update(kwargs)

        raw = yaml.dump(*args, **final_kwargs)
        if raw.endswith(suffix):
            raw = raw[suffix_slice]
        return raw

    return dump


def yaml_decoder_factory():
    """ Return a callable that decodes YAML. """
    return partial(yaml.load, Loader=loader_factory)


def dumper_factory(*args, **kwargs):
    """ Return a `yaml.Dumper` that correctly handles some special classes like
    TraitSetObject. """
    dumper = yaml.Dumper(*args, **kwargs)
    dumper.add_representer(TraitSetObject, yaml.Dumper.represent_set)
    dumper.add_representer(TraitListObject, yaml.Dumper.represent_list)
    dumper.add_representer(TraitDictObject, yaml.Dumper.represent_dict)
    dumper.add_representer(UUID, _represent_uuid)
    dumper.add_implicit_resolver(YAML_TAG_UUID, UUID_REGEX, None)
    dumper.add_representer(Blob, _represent_blob)
    return dumper


def loader_factory(*args, **kwargs):
    """ Return a `yaml.Loader` that can construct objects encoded by
    `yaml.Decoder` produced by `dumper_factory`. """
    loader = yaml.Loader(*args, **kwargs)
    loader.add_constructor(YAML_TAG_UUID, _construct_uuid)
    loader.add_implicit_resolver(YAML_TAG_UUID, UUID_REGEX, None)
    loader.add_constructor(YAML_TAG_BLOB, _construct_blob)
    return loader


@provides(IObjectStore)
class YAMLObjectStore(HasTraits):

    """ An IObjectStore backed by a YAML file. """

    #: The filename of the YAML storage on disk
    filename = File(os.path.join(tempfile.gettempdir(), 'object_store.yaml'))

    #: A Callable that turns values into YAML
    _encode = Callable

    #: A Callable that turns YAML into values
    _decode = Callable

    #: A python representation of the YAML file
    _disk_mirror = Dict

    def __encode_default(self):
        return yaml_encoder_factory()

    def __decode_default(self):
        return yaml_decoder_factory()

    def set(self, key, value):
        """ Associate `value` with `key` and update the YAML file. """
        self._disk_mirror[key] = value
        with open(self.filename, 'w') as fp:
            fp.write(self._encode(self._disk_mirror))
        return

    def get(self, key):
        """ Retrieve the value associated with `key`. """
        with open(self.filename, 'r') as fp:
            data = fp.read()
        self._disk_mirror = self._decode(data)
        return self._disk_mirror[key]
