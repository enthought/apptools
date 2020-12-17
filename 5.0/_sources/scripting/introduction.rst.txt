.. _automatic-script-recording:

Automatic script recording
===========================

This package provides a very handy and powerful Python script recording
facility.  This can be used to:

 - record all actions performed on a traits based UI into a *human
   readable*, Python script that should be able to recreate your UI
   actions.

 - easily learn the scripting API of an application.

This package is not just a toy framework and is powerful enough to
provide full script recording to the Mayavi_ application.  Mayavi is a
powerful 3D visualization tool that is part of ETS_.

.. _Mayavi: https://docs.enthought.com/mayavi/mayavi/
.. _ETS: https://docs.enthought.com/ets/

.. _scripting-api:


The scripting API
------------------

The scripting API primarily allows you to record UI actions for objects
that have Traits.  Technically the framework listens to all trait
changes so will work outside a UI.  We do not document the full API
here, the best place to look for that is the
``apptools.scripting.recorder`` module which is reasonably well
documented.  We provide a high level overview of the library.

The quickest way to get started is to look at a small example.


.. _scripting-api-example:

A tour by example
~~~~~~~~~~~~~~~~~~~

The following example is taken from the test suite.  Consider a set of
simple objects organized in a hierarchy::

    from traits.api import (HasTraits, Float, Instance,
            Str, List, Bool, HasStrictTraits, Tuple, PrefixMap, Range,
            Trait)
    from apptools.scripting.api import (Recorder, recordable,
        set_recorder)

    class Property(HasStrictTraits):
        color = Tuple(Range(0.0, 1.0), Range(0.0, 1.0), Range(0.0, 1.0))
        opacity = Range(0.0, 1.0, 1.0)
        representation = PrefixMap(
            {"surface": 2, "wireframe": 1, "points": 0},
            default_value="surface"
        )

    class Toy(HasTraits):
        color = Str
        type = Str
        # Note the use of the trait metadata to ignore this trait.
        ignore = Bool(False, record=False)

    class Child(HasTraits):
        name = Str('child')
        age = Float(10.0)
        # The recorder walks through sub-instances if they are marked
        # with record=True
        property = Instance(Property, (), record=True)
        toy = Instance(Toy, record=True)
        friends = List(Str)

        # The decorator records the method.
        @recordable
        def grow(self, x):
            """Increase age by x years."""
            self.age += x

    class Parent(HasTraits):
        children = List(Child, record=True)
        recorder = Instance(Recorder, record=False)

Using these simple classes we first create a simple object hierarchy as
follows::

    p = Parent()
    c = Child()
    t = Toy()
    c.toy = t
    p.children.append(c)

Given this hierarchy, we'd like to be able to record a script.  To do
this we setup the recording infrastructure::

    from mayavi.core.recorder import Recorder, set_recorder
    # Create a recorder.
    r = Recorder()
    # Set the global recorder so the decorator works.
    set_recorder(r)
    r.register(p)
    r.recording = True

The key method here is the ``r.register(p)`` call above.  It looks at
the traits of ``p`` and finds all traits and nested objects that specify
a ``record=True`` in their trait metadata (all methods starting and
ending with ``_`` are ignored).  All sub-objects are in turn registered
with the recorder and so on.  Callbacks are attached to traits changes
and these are wired up to produce readable and executable code.  The
``set_recorder(r)`` call is also very important and sets the global
recorder so the framework listens to any functions that are decorated
with the ``recordable`` decorator.

Now lets test this out like so::

    # The following will be recorded.
    c.name = 'Shiva'
    c.property.representation = 'w'
    c.property.opacity = 0.4
    c.grow(1)

To see what's been recorded do this::

    print(r.script)

This prints::

    child = parent.children[0]
    child.name = 'Shiva'
    child.property.representation = 'wireframe'
    child.property.opacity = 0.40000000000000002
    child.grow(1)

The recorder internally maintains a mapping between objects and unique
names for each object.  It also stores the information about the
location of a particular object in the object hierarchy.  For example,
the path to the ``Toy`` instance in the hierarchy above is
``parent.children[0].toy``.  Since scripting with lists this way can be
tedious, the recorder first instantiates the ``child``::

    child = parent.children[0]

Subsequent lines use the ``child`` attribute.  The recorder always tries
to instantiate the object referred to using its path information in this
manner.

To record a function or method call one must simply decorate the
function/method with the ``recordable`` decorator.  Nested recordable
functions are not recorded and trait changes are also not recorded if
done inside a recordable function.

.. note::

    1. It is very important to note that the global recorder must be set
       via the ``set_recorder`` method.  The ``recordable`` decorator
       relies on this being set to work.

    2. The ``recordable`` decorator will work with plain Python classes
       and with functions too.

To stop recording do this::

    r.unregister(p)
    r.recording = False

The ``r.unregister(p)`` reverses the ``r.register(p)`` call and
unregisters all nested objects as well.


.. _recorder-advanced-uses:

Advanced use cases
~~~~~~~~~~~~~~~~~~~~

Here are a few advanced use cases.

 - The API also provides a ``RecorderWithUI`` class that provides a
   simple user interface that prints the recorded script and allows the
   user to save the script.

 - Sometimes it is not enough to just record trait changes, one may want
   to pass an arbitrary string or command when recording is occurring.
   To allow for this, if one defines a ``recorder`` trait on the object,
   it is set to the current recorder.  One can then use this recorder to
   do whatever one wants.  This is very convenient.

 - To ignore specific traits one must specify either a ``record=False``
   metadata to the trait definition or specify a list of strings to the
   ``register`` method in the ``ignore`` keyword argument.

 - If you want to use a specific name for an object on the script you
   can pass the ``script_id`` parameter to the register function.


For more details on the recorder itself we suggest reading the module
source code.  It is fairly well documented and with the above background
should be enough to get you going.
