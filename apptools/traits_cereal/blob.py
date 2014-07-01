#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uuid import UUID, uuid4

from traits.api import Dict, Either, HasTraits, Instance, Int, Set, Str

from .utils import class_qualname


def blob_skeleton(obj, key_factory=None, **kwargs):
    """ Return a Blob with the correct `class_name` for `obj` and default
    values elsewhere. """

    defaults = {
        'version': 1,
        # Py3 introduces this for real in __qualname__. If we don't want to
        # implement lots of wrapper adapters we have to do it this way.
        'class_name': class_qualname(obj),
    }

    if key_factory is not None:
        defaults['obj_key'] = key_factory(obj)
    else:
        defaults['obj_key'] = uuid4()

    defaults.update(kwargs)

    return Blob(**defaults)


class Blob(HasTraits):
    """ A low-level object that has just come from the ether and represents
    an object to be reified. """

    #: The key used to store this blob
    obj_key = Either(Str, Instance(UUID))

    #: The fully qualified class name of the object this blob represents
    class_name = Str

    #: The version of the storage protocol used to create this blob
    version = Int

    #: The deflated object's attributes with child objects replaced by keys
    obj_attrs = Dict

    #: The set of serializable objects represented by the keys in `obj_attrs`
    children = Set()

    def __str__(self):
        return "<Blob of {}({})>".format(self.class_name, self.obj_key)

    def __repr__(self):
        msg = ("Blob(obj_key={obj_key!r}, class_name={class_name!r}, "
               "version={version!r}, obj_attrs={obj_attrs!r}, "
               "children={children!s})")
        return msg.format(**self.get())

    def __eq__(self, other):
        if not hasattr(other, 'get'):
            return False
        return self.get() == other.get()
