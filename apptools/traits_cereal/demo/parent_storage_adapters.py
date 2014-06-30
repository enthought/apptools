#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apptools.traits_cereal.traits.api import Instance, provides
from apptools.traits_cereal.traits.adaptation.adaptation_manager import (
    adaptation_manager as GLOBAL_ADAPTATION_MANAGER)

from storables import Parent
from apptools.traits_cereal.storage_manager import IDeflatable, IInflatable, Blob
from apptools.traits_cereal.default_storage_adapters import (
    DefaultDeflator, DefaultInflator)


@provides(IDeflatable)
class ParentToIDeflatable(DefaultDeflator):
    class_name = 'Parent'
    version = 2
    adaptee = Instance(Parent)

    def deflate(self):
        blob = super(ParentToIDeflatable, self).deflate()
        # Could change blob.class_name here
        return blob


@provides(IInflatable)
class ParentToIInflatable1(DefaultInflator):
    adaptee = Instance(Blob)

    def inflate(self, get_obj_by_uuid, reify=True):
        print("Loading Parent v1")
        self.adaptee = super(ParentToIInflatable1, self).inflate(
            get_obj_by_uuid, reify=False)
        return Parent(**self.adaptee.attrs)


@provides(IInflatable)
class ParentToIInflatable2(DefaultInflator):
    adaptee = Instance(Blob)

    def inflate(self, get_obj_by_uuid, reify=True):
        print("Loading Parent v2")
        self.adaptee = super(ParentToIInflatable2, self).inflate(
            get_obj_by_uuid, reify=False)
        return Parent(**self.adaptee.attrs)


PARENT_DESERIALIZERS = {
    1: ParentToIInflatable1,
    2: ParentToIInflatable2
}


def parent_to_IInflatable(adaptee):
    # class_name is potentially fully qualified.
    # We should discuss if this will make any sense or not long term.
    if adaptee.class_name.endswith('Parent'):
        factory = PARENT_DESERIALIZERS[adaptee.version]
        return factory(adaptee=adaptee)


def register_adapters(adaptation_manager=GLOBAL_ADAPTATION_MANAGER):
    adaptation_manager.register_factory(
        ParentToIDeflatable, Parent, IDeflatable)
    adaptation_manager.register_factory(
        parent_to_IInflatable, Blob, IInflatable)
