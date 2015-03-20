Application Scripting Framework
===============================

The Application Scripting Framework is a component of the Enthought Tool Suite
that provides developers with an API that allows traits based objects to be
made scriptable.  Operations on a scriptable object can be recorded in a
script and subsequently replayed.

The framework is completely configurable.  Alternate implementations of all
major components can be provided if necessary.


Framework Concepts
------------------

The following are the concepts supported by the framework.

- Scriptable Type

  A scriptable type is a sub-type of ``HasTraits`` that has scriptable methods
  and scriptable traits.  If a scriptable method is called, or a scriptable
  trait is set, then that action can be recorded in a script and subsequently
  replayed.

  If the ``__init__()`` method is scriptable then the creation of an object
  from the type can be recorded.

  Scriptable types can be explicitly defined or created dynamically from any
  sub-type of ``HasTraits``.

- Scriptable API

  The set of a scriptable type's scriptable methods and traits constitutes the
  type's scriptable API.

  The API can be defined explicitly using the ``scriptable`` decorator (for
  methods) or the ``Scriptable`` wrapper (for traits).

  For scriptable types that are created dynamically then the API can be
  defined in terms of one or more types or interfaces or an explicit list of
  method and trait names.  By default, all public methods and traits (ie.
  those whose name does not begin with an underscore) are part of the API.  It
  is also possible to then explicitly exclude a list of method and trait
  names.

- Scriptable Object

  A scriptable object is an instance of a scriptable type.

  Scriptable objects can be explicitly created by calling the scriptable type.
  Alternatively a non-scriptable object can be made scriptable dynamically.

- Script

  A script is a Python script and may be a recording or written from scratch.

  If the creation of scriptable objects can be recorded, then it may be
  possible for a recording to be run directly by the Python interpreter and
  independently of the application that made the recording.  Otherwise the
  application must run the script and first create any scriptable objects
  refered to in the script.

- Binding

  A script runs in a namespace which is, by default, empty.  If the scriptable
  objects refered to in a script are not created by the script (because their
  type's ``__init__()`` method isn't scriptable) then they must be created by
  the application and added to the namespace.  Adding an object to the
  namespace is called binding.

  Scriptable objects whose creation can be recorded will automatically bind
  themselves when they are created.

  It also possible to bind an object factory rather than the object itself.
  The factory will be called, and the object created, only if the object is
  needed by the script when it is run.  This is typically used by plugins.

  The name that an object is bound to need bear no relation to the object's
  name within the application.  Names may be dotted names (eg. ``aaa.bbb.ccc``)
  and appropriate objects representing the intermediate parts of such a name
  will be created automatically.

  An event is fired whenever an object is bound (or when a bound factory is
  invoked).  This allows other objects (eg. an embedded Python shell) to
  expose scriptable objects in other ways.

- Script Manager

  A script manager is responsible for the recording and subsequent playback of
  scripts.  An application has a single script manager instance which can be
  explicitly set or created automatically.


Limitations
-----------

In the current implementation scriptable Trait container types (eg. List,
Dict) may only contain objects corresponding to fundamental Python types (eg.
int, bool, str).


API Overview
------------

This section gives an overview of the API implemented by the framework.  The
complete API_ documentation is available as endo generated HTML.

The example_ application demonstrates some the features of the framework.


Module Level Objects
....................

``get_script_manager()``
    The application's script manager is returned.  One will be created
    automatically if needed.

``set_script_manager(script_manager)``
    The application's script manager will be set to ``script_manager``
    replacing any existing script manager.

``scriptable``
    This is a decorator used to explicitly mark methods as being scriptable.
    Any call to a scriptable method is recorded.  If a type's ``__init__()``
    method is decorated then the creation of the object will be recorded.

``Scriptable``
    This is a wrapper for a trait to explicitly mark it as being scriptable.
    Any change to the value of the trait will be recorded.  Simple reads of the
    trait will not be recorded unless unless the value read is bound to another
    scriptable trait or passed as an argument to a scriptable method.  Passing
    ``has_side_effects=True`` when wrapping the trait will ensure that a read
    will always be recorded.

``create_scriptable_type(script_type, name=None, bind_policy='auto', api=None, includes=None, excludes=None, script_init=True)``
    This creates a new type based on an existing type but with certain methods
    and traits marked as being scriptable.  Scriptable objects can then be
    created by calling the type.

    ``script_type`` is the existing, non-scriptable, type.  The new type will
    be a sub-type of it.  The ``api``, ``includes`` and ``excludes`` arguments
    determine which methods and traits are made scriptable.  By default, all
    public methods and traits (ie. those whose name does not begin with an
    underscore) are made scriptable.

    The ``name`` and ``bind_policy`` arguments determine how scriptable
    objects are bound when they are created.  ``name`` is the name that an
    object will be bound to.  It defaults to the name of ``script_type`` with
    the first character forced to lower case.  ``name`` may be a dotted name,
    eg. ``aaa.bb.c``.

    ``bind_policy`` determines what happens if an object is already bound to
    the name.  If it is ``auto`` then a numerical suffix will be added to the
    name of the new object.  If it is ``unique`` then an exception will be
    raised.  If it is ``rebind`` then the object currently bound to the name
    will be unbound.

    ``api`` is a class or interface (or a list of classes or interfaces) that
    is used to provide the names of the methods and traits to be made
    scriptable.  The class or interface effectively defines the scripting API.

    If ``api`` is not specified then ``includes`` is a list of method and
    trait names that are made scriptable.

    If ``api`` and ``includes`` are not specified then ``excludes`` is a list
    of method and trait names that are *not* made scriptable.

    If ``script_init`` is set then the ``__init__()`` method is made scriptable
    irrespective of the ``api``, ``includes`` and ``excludes`` arguments.

    If ``script_init`` is not set then objects must be explicitly bound and
    ``name`` and ``bind_policy`` are ignored.

``make_object_scriptable(obj, api=None, includes=None, excludes=None)``
    This takes an existing unscriptable object and makes it scriptable.  It
    works by calling ``create_scriptable_type()`` on the the objects existing
    type and replacing that existing type with the new scriptable type.

    See the description of ``create_scriptable_type()`` for an explanation of
    the ``api``, ``includes`` and ``excludes`` arguments.


ScriptManager
.............

The ``ScriptManager`` class is the default implementation of the
``IScriptManager`` interface.

``bind_event``
    This event is fired whenever an object is bound or unbound.  The event's
    argument implements the ``IBindEvent`` interface.

``recording``
    This trait is set if a script is currently being recorded.  It is updated
    automatically by the script manager.

``script``
    This trait contains the text of the script currently being recorded (or
    the last recorded script if one is not being currently recorded).  It is
    updated automatically by the script manager.

``script_updated``
    This event is fired whenever the ``script`` trait is updated.  The event's
    argument is the script manager.

``bind(self, obj, name=None, bind_policy='unique', api=None, includes=None, excludes=None)``
    This method makes an object scriptable and binds it to a name.  See the
    description of ``create_scriptable_type()`` for an explanation of the
    ``api``, ``includes``, ``excludes``, ``name`` and ``bind_policy``
    arguments.

``bind_factory(self, factory, name, bind_policy='unique', api=None, includes=None, excludes=None)``
    This method binds an object factory to a name.  The factory is called to
    create the object (and make it scriptable) only when the object is needed
    by a running script.  See the description of ``create_scriptable_type()``
    for an explanation of the ``name`` and ``bind_policy`` arguments.

``run(self, script)``
    This method runs a script in a namespace containing all currently bound
    objects.  ``script`` is any object that can be used by Python's ``exec``
    statement including a string or a file-like object.

``run_file(self, file_name)``
    This method runs a script in a namespace containing all currently bound
    objects.  ``file_name`` is the name of a file containing the script.

``start_recording(self)``
    This method starts the recording of a script.

``stop_recording(self)``
    This method stops the recording of the current script.


IBindEvent
..........

The ``IBindEvent`` interface defines the interface that is implemented by the
object passed when the script manager's ``bind_event`` is fired.

``name``
    This trait is the name being bound or unbound.

``obj``
    This trait is the obj being bound to ``name`` or None if ``name`` is being
    unbound.


StartRecordingAction
....................

The ``StartRecordingAction`` class is a canned PyFace action that starts the
recording of changes to scriptable objects to a script.


StopRecordingAction
...................

The ``StopRecordingAction`` class is a canned PyFace action that ends the
recording of changes to scriptable objects to a script.


Implementing Application Scripting
----------------------------------

The key part of supporting application scripting is to design an appropriate
scripting API and to ensure than the application itself uses the API so that
changes to the data can be recorded.  The framework provides many ways to
specify the scripting API.  Which approach is appropriate in a particular case
will depend on when it is a new application, or whether scripting is being
added to an existing application, and how complex the application's data model
is.

Static Specification
....................

A scripting API is specified statically by the explicit use of the
``scriptable`` decorator and the ``Scriptable`` trait wrapper.  For example::

    from apptools.appscripting.api import scriptable, Scriptable
    from traits.api import HasTraits, Int, Str

    class DataModel(HasTraits):

        foo = Scriptable(Str)

        bar = Scriptable(Int, has_side_effects=True)

        @scriptable
        def baz(self):
            pass

        def weeble(self)
            pass

    # Create the scriptable object.  It's creation won't be recorded because
    # __init__() isn't decorated.
    obj = DataModel()

    # These will be recorded.
    obj.foo = ''
    obj.bar = 10
    obj.baz()

    # This will not be recorded.
    obj.weeble()

    # This won't be recorded unless 'f' is passed to something that is
    # recorded.
    f = obj.foo

    # This will be recorded because we set 'has_side_effects'.
    b = obj.bar


Dynamic Specification
.....................

A scripting API can also be specified dynamically.  The following example
produces a scriptable object with the same scriptable API as above (with the
exception that ``has_side_effects`` cannot be specified dynamically)::

    from apptools.appscripting.api import create_scriptable_type
    from traits.api import HasTraits, Int, Str

    class DataModel(HasTraits):

        foo = Str

        bar = Int

        def baz(self):
            pass

        def weeble(self)
            pass

    # Create a scriptable type based on the above.
    ScriptableDataModel = create_scriptable_type(DataModel, excludes=['weeble'])

    # Now create scriptable objects from the scriptable type.  Note that each
    # object has the same type.
    obj1 = ScriptableDataModel()
    obj2 = ScriptableDataModel()

Instead we could bypass the type and make the objects themselves scriptable as
follows::

    from apptools.appscripting.api import make_object_scriptable
    from traits.api import HasTraits, Int, Str

    class DataModel(HasTraits):

        foo = Str

        bar = Int

        def baz(self):
            pass

        def weeble(self)
            pass

    # Create unscriptable objects.
    obj1 = DataModel()
    obj2 = DataModel()

    # Now make the objects scriptable.  Note that each object has a different
    # type, each a sub-type of 'DataModel'.
    make_object_scriptable(obj1, excludes=['weeble'])
    make_object_scriptable(obj2, excludes=['weeble'])

With a more sophisticated design we may choose to specify the scriptable API as
an interface as follows::

    from apptools.appscripting.api import make_object_scriptable
    from traits.api import HasTraits, Int, Interface, Str

    class DataModel(HasTraits):

        foo = Str

        bar = Int

        def baz(self):
            pass

        def weeble(self)
            pass

    class IScriptableDataModel(Interface):

        foo = Str

        bar = Int

        def baz(self):
            pass

    # Create an unscriptable object.
    obj = DataModel()

    # Now make the object scriptable.
    make_object_scriptable(obj, api=IScriptableDataModel)


Scripting __init__()
....................

Making a type's ``__init__()`` method has advantages and disadvantages.  It
means that the creation of scriptable objects will be recorded in a script
(along with the necessary ``import`` statements).  This means that the script
can be run independently of your application by the standard Python
interpreter.

The disadvantage is that, if you have a complex data model, with many
interdependencies, then defining a complete and consistent scripting API that
allows a script to run independently may prove difficult.  In such cases it is
better to have the application create and bind the scriptable objects itself.


.. _API: api/index.html
.. _example: https://svn.enthought.com/enthought/browser/AppTools/trunk/examples/appscripting/
