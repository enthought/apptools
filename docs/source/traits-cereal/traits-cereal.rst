=================================
Traits Cereal: Object Persistence
=================================

This document describes a system for the serialization and persistence of
HasTraits objects. Zooming way out, the storage system looks like this:

.. graphviz:: traits-cereal-overview.gv


Requirements
============

The state of the application should be storable and loadable such that a
session created by loading a project is functionally indistinguishable from the
session that it was saved from. To achieve this, the state of the application
should be specifiable as a directed graph, with nodes representing
``HasTraits`` instances and primitive data and edges representing attribute
membership.

The Graph
---------

If two objects are instantiated in the application, and object A has a
reference to object B as an explicit attribute on object A, we can say that
there is an edge from A to B because A is dependent on the instantiation of B
before it can be instantiated itself. There is probably no need to explicitly
write out such a graph, but acknowledging it conceptually might help with the
resolution of problems such as loading and instantiating a complicated
hierarchy of classes from disk.

An organizational problem arises when we consider the idea of classes with
attributes that are *required* at instantiation. If we are willing to assert
that no classes with customized ``__init__`` methods can be serialized, then
the serialization machinery will be much less complex and less likely to
fail/dead-lock when circular dependencies are encountered.

Alternatively, we can require that there are no cycles in the object graph,
i.e. no children have references to their parents. In such a case, it will be
OK for the loading of an object to block entirely until all children have fully
loaded. **This draft assumes the latter for now.**


Storage Interfaces
==================

Each serializable object is expected to implement or have an adapter for some
aptly named interfaces such as ``IDeflatable`` and ``IInflatable``::

    class IDeflatable(Interface):

        adaptee = Any
        version = Int

        def deflate(self, get_or_create_key):
           """Return a Blob representation of the adaptee."""

    class IInflatable(Interface):

        adaptee = Instance(Blob)
        version = Int

        def inflate(self, get_obj_by_key):
           """Return the object tagged with the key in the adaptee Blob,
           reifying it and its children from disk if necessary.

           If this function has been called once before, it must *not* be
           called again in such a way that creates a second instance of the
           object. This is typically handled by caching in the
           ``StorageManager``.
           """

Separate interfaces are used for saving and loading to maintain backwards
compatibility. Saving is only necessary for the latest version and all projects
are implicitly updated to that version when they pass through a load/save
round trip.


Saving
======

Saving of an object is split into two steps. The initial step, handled by the
interfaces described above converts the object to a ``Blob`` object shown
below::

    class Blob(HasTraits):
        """ This is a low-level object that serves to unify the API of all
        objects on their way to and from the ``IObjectStore``.

        Parameters:

        obj_key : Either(Str, uuid.UUID)
            The UUID or key-string of the object that this Blob represents.

        class_name : str
            The fully qualified class name of the object that this Blob
            represents, e.g. "foo.bar.quux.Quux".

        version : int
            The version of the serializer that was used to create this Blob.

        attrs : dict
            The attribute dictionary of the object that this Blob represents.
            All serializable objects in this dictionary are replaced with the
            key of that object.

        children : set
            During saving, this is the set of child objects that were removed
            from attrs and replaced by their keys. These objects must all be
            persisted for this Blob to be considered correctly persisted.

            During loading, this is the set of keys found in attrs. These
            keys must all be loaded before we try to load this Blob.
        """

        obj_key = Either(Str, Instance(UUID))
        class_name = Str
        version = Int

        # Attributes with serializable objects replaced by keys
        attrs = Dict

        # A set of serializable objects that must also be handled for this blob
        # to be considered persisted.
        children = Set()


``Blob.attrs`` is created via a shallow traversal of the attributes of the
object being persisted, adding all serializable objects to ``Blob.children``
and replacing them with their keys.

After the Blob has been constructed, we must create Blobs for all objects in
``Blob.children`` and pass them to the ``StorageManager`` to be written out to
storage, then this Blob can finally be passed to the ``StorageManager`` itself.

This should completely separate the on-disk layout of the objects from their
serialization and allow us to safely change the storage system without breaking
saving and loading. By not requiring objects on disk to reflect the same
hierarchy as objects in memory, it gives us the flexibility to prevent the same
object from being saved in multiple locations due to multiple references to
that object existing.

Careful attention needs to be paid to avoiding redundant work when saving the
objects themselves. The ``StorageManager`` can track which ``Blob``
objects it has already seen and handled during this call to ``save``.


Loading
=======

The loading of an object from disk proceeds like saving in reverse. The
``StorageManager`` must first produce a ``Blob`` object from remote storage. It
is assumed that this will be possible by simply inspecting the node at which
the blob data has been serialized.

Each keys present in ``Blob.children`` is requested before proceeding to
produce references to all of the objects that will be needed to populate
``Blob.attrs``. We can then traverse ``Blob.attrs``, replacing keys with their
objects. Once this is done, we can pass ``Blob.attrs`` to the object's
constructor (defined in ``Blob.class_name``) and reify the object.

We should now have the real object again, in the same state it was in when it
was saved, including maintaining the same key.

Further calls to load this object's key will produce *this same instance* of
the object. The ``StorageManager`` should handle this by caching loaded objects
in a ``weakref.WeakValueDictionary`` or something similar.

This is a slightly simplified description of what needs to happen. In a more
complicated case, such as when there are circular dependencies, some notion of
partial or lazy loading of object instances will be necessary.


API Changes
===========

When API of a deflatable object or its on-disk representation changes, the
adapters that provide the ``IDeflatable`` and ``IInflatable`` interfaces
must potentially change with it.

**Any change to these adapters must be accompanied by a version bump!**

As an example work flow, let's take a class ``Foo`` and adapt it to our storage
scheme. First, some setup. We define our class and an opaque ``Blob`` class to
serve as an intermediary layer. ::

    from traits.api import (
        Dict, HasTraits, Int, Instance, Interface, provides, String)
    from traits.adaptation.api import adapt, Adapter, register_factory


    class Foo(HasTraits):
        """ The class we would like to serialize/deserialize"""
        bar = Int
        _baz = Dict

Then we write ``Adapter`` classes to provide this functionality to our ``Foo``
class. To maintain backwards compatibility, there is an ``IInflatable``
adapter for each version of ``Foo`` that has ever been deflated. Since we
only care about storing data in the most current scheme, we only need one
``IDeflatable`` adapter.

Every object that needs to be stored on disk will pass through the interfaces
described earlier, although a default implementation is provided that will
*probably* work if one does not exist for the class. For convenience, the
defaults can be subclassed modified further before returning the deflated
``Blob``. ::

    # Adaptation ##############################################################

    @provides(IDeflatable)
    class FooToIDeflatable(DefaultDeflator):
        version = 2
        adaptee = Instance(Foo)

        def deflate(self, get_or_create_uuid):
            # Let's pretend we aren't interested in saving `_baz`
            blob = super(FooToIDeflatable, self).deflate(get_or_create_uuid)
            blob.attrs.pop('_baz')


    @provides(IInflatable)
    class FooToIInflatableV1(Adapter):
        adaptee = Instance(Blob)

        def inflate(self, get_obj_by_uuid):
            print("Inflating V1")
            super(FooToIInflatable, self).inflate(get_obj_by_uuid)
            # In version we saved `_baz`, we should remove it now
            self.adaptee.attrs.pop('_baz')
            return Foo(**self.adaptee.attrs)


    @provides(IInflatable)
    class FooToIInflatableV2(Adapter):
        adaptee = Instance(Blob)

        def inflate(self, get_obj_by_uuid):
            print("Inflating V2")
            super(FooToIInflatable, self).inflate(get_obj_by_uuid)
            # In version 2 we didn't save `_baz`, no further action needed
            return Foo(**self.adaptee.attrs)

We'll use Traits' conditional adaptation to handle finding the right inflator
for each ``Blob``. An adapter factory is defined which inspects the ``Blob``
and adapts it to ``IInflator`` if possible. If no inflator adapter matches
the type and version of this ``Blob``, we return ``None`` and allow Traits to
continue searching. ::

    inflators = {
        1: FooToIInflatableV1,
        2: FooToIInflatableV2
    }


    def foo_to_IInflator(adaptee):
        # Probably want fully qualified class here
        if adaptee.class_name.endswith('Foo'):
            factory = inflators.get(adaptee.version)
            return factory(adaptee=adaptee) if factory else None
        else:
            return None

    register_factory(FooToIDeflatable, Foo, IDeflatable)
    register_factory(foo_to_IInflatable, Blob, IInflatable)


Seed Points
===========

Our preference is to avoid serializing an entire tree of objects when only a
simple instance is needed. For example, the configuration for the view on an
annotation might be saved, but we don't need to save the annotation manager, or
some such similar object that serves as a container for annotations.

This causes a problem. We want to serialize state, but we don't want the parent
object to know what *exactly* was serialized. If we kept the key of the
serialized object, we'd then have to serialize the parent as well or the key
would be forgotten on restart.

To maneuver around this, we will require that loading (and thus saving) occurs
at few "seed points" which are known in advance and **unique within the
application**. A seed point is then associated with a magic key which is used
in place of an auto-generated key for that unique object. The parent of this
object will not construct the object themselves, but instead will simply
request the object associated with its magic key from the data store. If the
object has been stored, it will be returned, otherwise it will be created and
returned.

A small example::

    Class BaboonCorral(HasTraits):
        """ The corral in which all Baboons in the application live. """

        baboons = List(Baboon)


    Class Zoo(HasTraits):
        baboon_corral = Instance(BaboonCorral)

        def _baboon_corral_default(self):
            # The baboon corral is unique and tracked by the storage manager
            storage_manager.get_or_create("BaboonCorral")

The call to ``get_or_create`` will give back a default ``BaboonCorral`` if none
has been previously stored, otherwise it will begin the cascade of loading
calls required to bring the stored ``BaboonCorral`` back to life.


Examples
========

A more comprehensive example is found in ``apptools.traits_cereal.demo``.
