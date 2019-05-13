#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Riverbank Computing Limited
# Description: <Enthought application scripting package component>
#------------------------------------------------------------------------------


# Standard library imports.
import datetime
import types
import weakref

# Enthought library imports.
from traits.api import Any, Bool, Callable, Dict, Event, HasTraits, \
        implements, Instance, Int, List, Property, Str, Unicode

# Local imports.
from .bind_event import BindEvent
from .i_bind_event import IBindEvent
from .i_script_manager import IScriptManager
from .lazy_namespace import add_to_namespace, FactoryWrapper, LazyNamespace
from .scriptable_type import make_object_scriptable


@provides(IScriptManager)
class _BoundObject(HasTraits):
    """The base class for any object that can be bound to a name."""

    #### '_BoundObject' interface #############################################

    # Set if the object was explicitly bound.
    explicitly_bound = Bool(True)

    # The name the object is bound to.
    name = Str

    # The object being bound.
    obj = Any


class _ScriptObject(_BoundObject):
    """The _ScriptObject class encapsulates a scriptable object."""

    #### '_BoundObject' interface #############################################

    # The object being bound.
    obj = Property

    #### '_ScriptObject' interface ############################################

    # The positional arguments passed to __init__ after being converted to
    # strings.  A particular argument may be an exception if it couldn't be
    # converted.
    args = List

    # The keyword arguments passed to __init__ after being converted to
    # strings.  A particular argument may be an exception if it couldn't be
    # converted.
    kwargs = Dict

    # The id of the object.
    obj_id = Int

    # A weak reference to the object.
    obj_ref = Any

    # The type of the scriptable object.
    scripted_type = Any

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _get_obj(self):
        """The property getter."""

        return self.obj_ref()


class _ScriptCall(HasTraits):
    """ The _ScriptCall class is the base class for all script calls. """

    #### '_ScriptCall' interface ##############################################

    # The name of the call.
    name = Str

    # The scriptable object.
    so = Any

    ###########################################################################
    # '_ScriptCall' interface.
    ###########################################################################

    def as_str(self, sm, so_needed):
        """ Return the string equivalent of the call, updated the list of
        needed scriptable objects if required.
        """

        raise NotImplementedError


class _ScriptTraitGet(_ScriptCall):
    """ The _ScriptTraitGet class encapsulates a single call to the get of a
    scriptable trait.
    """

    #### '_ScriptTraitGet' interface ##########################################

    # Set if the getter has side effects.
    has_side_effects = Bool(False)

    # The result of the get.  Keeping a reference to it means that the memory
    # can't get reused.
    result = Any

    ###########################################################################
    # '_ScriptCall' interface.
    ###########################################################################

    def as_str(self, sm, so_needed):
        """ Return the string equivalent of the call, updated the list of
        needed scriptable objects if required.
        """

        # Ignore if it is no longer bound.
        if not self.so.name:
            return None

        if self.result is None:
            rstr = ""
        else:
            nr, _ = sm._results[id(self.result)]

            if nr >= 0:
                rstr = "r%d = " % nr
            else:
                rstr = ""

        # Unless getter has side effects, if the result is not needed then
        # don't bother including it in the script.
        if not self.has_side_effects and rstr == "":
            return None

        so = sm.arg_as_string(self.so, so_needed)

        return "%s%s.%s" % (rstr, so, self.name)


class _ScriptTraitSet(_ScriptCall):
    """ The _ScriptTraitSet class encapsulates a single call to the set of a
    scriptable trait.
    """

    #### '_ScriptTraitSet' interface ##########################################

    # The value the trait is set to.
    value = Any

    ###########################################################################
    # '_ScriptCall' interface.
    ###########################################################################

    def as_str(self, sm, so_needed):
        """ Return the string equivalent of the call, updated the list of
        needed scriptable objects if required.
        """

        # Ignore if it is no longer bound.
        if not self.so.name:
            return None

        so = sm.arg_as_string(self.so, so_needed)
        value = sm.arg_as_string(self.value, so_needed)

        return "%s.%s = %s" % (so, self.name, value)


class _ScriptMethod(_ScriptCall):
    """ The _ScriptMethod class encapsulates a single call to a scriptable
    method.
    """

    #### '_ScriptMethod' interface ############################################

    # The positional arguments passed to the method after being converted to
    # strings.  A particular argument may be an exception if it couldn't be
    # converted.
    args = List

    # The keyword arguments passed to the method after being converted to
    # strings.  A particular argument may be an exception if it couldn't be
    # converted.
    kwargs = Dict

    # The result of the method call.  Keeping a reference to it means that the
    # memory can't get reused.
    result = Any

    ###########################################################################
    # '_ScriptCall' interface.
    ###########################################################################

    def as_str(self, sm, so_needed):
        """ Return the string equivalent of the call, updated the list of
        needed scriptable objects if required.
        """

        # Ignore if it is no longer bound.
        if self.so and not self.so.name:
            return None

        if self.result is None:
            rstr = ""
        elif type(self.result) is type(()):
            rlist = []
            needed = False

            for r in self.result:
                nr, _ = sm._results[id(r)]

                if nr >= 0:
                    rlist.append("r%d" % nr)
                    needed = True
                else:
                    rlist.append("_")

            if needed:
                rstr = ", ".join(rlist) + " = "
            else:
                rstr = ""
        else:
            nr, _ = sm._results[id(self.result)]

            if nr >= 0:
                rstr = "r%d = " % nr
            else:
                rstr = ""

        if self.so:
            so = sm.arg_as_string(self.so, so_needed) + '.'
        else:
            so = ''

        args = sm.args_as_string_list(self.args, self.kwargs, so_needed)

        return "%s%s%s(%s)" % (rstr, so, self.name, ", ".join(args))


class _FactoryObject(_BoundObject):
    """ The _FactoryObject class wraps a factory that lazily creates
    scriptable objects.
    """

    #### '_BoundObject' interface #############################################

    # The object being bound.
    obj = Property

    #### '_FactoryObject' interface ###########################################

    # The optional object that defines the scripting API.
    api = Any

    # The scriptable object factory.
    factory = Callable

    # The optional attribute include list.
    includes = Any

    # The optional attribute exclude list.
    excludes = Any

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _get_obj(self):
        """The property getter."""

        return FactoryWrapper(factory=self.factory, api=self.api,
                includes=self.includes, excludes=self.excludes)


class ScriptManager(HasTraits):
    """ The ScriptManager class is the default implementation of
    IScriptManager.
    """



    #### 'IScriptManager' interface ###########################################

    # This event is fired whenever a scriptable object is bound or unbound.  It
    # is intended to be used by an interactive Python shell to give the
    # advanced user access to the scriptable objects.  If an object is created
    # via a factory then the event is fired when the factory is called, and not
    # when the factory is bound.
    bind_event = Event(IBindEvent)

    # This is set if user actions are being recorded as a script.  It is
    # maintained by the script manager.
    recording = Bool(False)

    # This is the text of the script currently being recorded (or the last
    # recorded script if none is currently being recorded).  It is updated
    # automatically as the user performs actions.
    script = Property(Unicode)

    # This event is fired when the recorded script changes.  The value of the
    # event will be the ScriptManager instance.
    script_updated = Event(IScriptManager)

    #### Private interface ####################################################

    # The list of calls to scriptable calls.
    _calls = List(Instance(_ScriptCall))

    # The dictionary of bound names.  The value is the next numerical suffix
    # to use when the binding policy is 'auto'.
    _names = Dict

    # The dictionary of _BoundObject instances keyed by the name the object is
    # bound to.
    _namespace = Dict

    # The next sequential result number.
    _next_result_nr = Int

    # The results returned by previous scriptable calls.  The key is the id()
    # of the result object.  The value is a two element tuple of the sequential
    # result number (easier for the user to use than the id()) and the result
    # object itself.
    _results = Dict

    # The dictionary of _ScriptObject instances keyed by the object's id().
    _so_by_id = Dict

    # The dictionary of _ScriptObject instances keyed by the a weak reference
    # to the object.
    _so_by_ref = Dict

    # The date and time when the script was recorded.
    _when_started = Any

    ###########################################################################
    # 'IScriptManager' interface.
    ###########################################################################

    def bind(self, obj, name=None, bind_policy='unique', api=None,
            includes=None, excludes=None):
        """ Bind obj to name and make (by default) its public methods and
        traits (ie. those not beginning with an underscore) scriptable.  The
        default value of name is the type of obj with the first character
        forced to lower case.  name may be a dotted name (eg. 'abc.def.xyz').

        bind_policy determines what happens if the name is already bound.  If
        the policy is 'auto' then a numerical suffix will be added to the name,
        if necessary, to make it unique.  If the policy is 'unique' then an
        exception is raised.  If the policy is 'rebind' then the previous
        binding is discarded.  The default is 'unique'

        If api is given then it is a class, or a list of classes, that define
        the attributes that will be made scriptable.

        Otherwise if includes is given it is a list of names of attributes that
        will be made scriptable.

        Otherwise all the public attributes of scripted_type will be made
        scriptable except those in the excludes list.
        """

        # Register the object.
        self.new_object(obj, obj.__class__, name=name, bind_policy=bind_policy)

        # Make it scriptable.
        make_object_scriptable(obj, api=api, includes=includes,
                excludes=excludes)

    def bind_factory(self, factory, name, bind_policy='unique', api=None,
            includes=None, excludes=None):
        """ Bind factory to name.  This does the same as the bind() method
        except that it uses a factory that will be called later on to create
        the object only if the object is needed.

        See the documentation for bind() for a description of the remaining
        arguments.
        """

        name = self._unique_name(name, bind_policy)
        self._namespace[name] = _FactoryObject(name=name, factory=factory,
                api=api, includes=includes, excludes=excludes)

    def run(self, script):
        """ Run the given script, either a string or a file-like object.
        """

        # Initialise the namespace with all explicitly bound objects.
        nspace = LazyNamespace()
        for name, bo in self._namespace.items():
            if bo.explicitly_bound:
                add_to_namespace(bo.obj, name, nspace)

        exec(script, nspace)

    def run_file(self, file_name):
        """ Run the given script file.
        """

        f = open(file_name)
        self.run(f)
        f.close()

    def start_recording(self):
        """ Start the recording of user actions.  The 'script' trait is cleared
        and all subsequent actions are added to 'script'.  The 'recording'
        trait is updated appropriately.
        """

        self._calls = []
        self._next_result_nr = 0
        self._results = {}

        self.recording = True
        self.script_updated = self

    def stop_recording(self):
        """ Stop the recording of user actions.  The 'recording' trait is
        updated appropriately.
        """

        self.recording = False

    ###########################################################################
    # 'ScriptManager' interface.
    ###########################################################################

    def record_method(self, func, args, kwargs):
        """ Record the call of a method of a ScriptableObject instance and
        return the result.  This is intended to be used only by the scriptable
        decorator.
        """
        if self.recording:
            # Record the arguments before the function has a chance to modify
            # them.
            srec = self._new_method(func, args, kwargs)
            result = func(*args, **kwargs)
            self._add_method(srec, result)

            self.script_updated = self
        else:
            result = func(*args, **kwargs)

        return result

    def record_trait_get(self, obj, name, result):
        """ Record the get of a trait of a scriptable object.  This is intended
        to be used only by the Scriptable trait getter.
        """

        if self.recording:
            side_effects = self._add_trait_get(obj, name, result)

            # Don't needlessly fire the event if there are no side effects.
            if side_effects:
                self.script_updated = self

    def record_trait_set(self, obj, name, value):
        """ Record the set of a trait of a scriptable object.  This is intended
        to be used only by the Scriptable trait getter.
        """

        if self.recording:
            self._add_trait_set(obj, name, value)

            self.script_updated = self

    def new_object(self, obj, scripted_type, args=None, kwargs=None, name=None,
            bind_policy='auto'):
        """ Register a scriptable object and the arguments used to create it.
        If no arguments were provided then assume the object is being
        explicitly bound.
        """

        # The name defaults to the type name.
        if not name:
            name = scripted_type.__name__
            name = name[0].lower() + name[1:]

        name = self._unique_name(name, bind_policy)

        obj_id = id(obj)
        obj_ref = weakref.ref(obj, self._gc_script_obj)

        so = _ScriptObject(name=name, obj_id=obj_id, obj_ref=obj_ref,
                scripted_type=scripted_type)

        # If we are told how to create the object then it must be implicitly
        # bound.
        if args is not None:
            # Convert each argument to its string representation if possible.
            # Doing this now avoids problems with mutable arguments.
            so.args = [self._scriptable_object_as_string(a) for a in args]

            for n, value in kwargs.items():
                so.kwargs[n] = self._scriptable_object_as_string(value)

            so.explicitly_bound = False

        # Remember the scriptable object via the different access methods.
        self._so_by_id[obj_id] = so
        self._so_by_ref[obj_ref] = so
        self._namespace[name] = so

        # Note that if anything listening to this event doesn't use weak
        # references then the object will be kept alive.
        self.bind_event = BindEvent(name=name, obj=obj)

    @staticmethod
    def args_as_string_list(args, kwargs, so_needed=None):
        """ Return a complete argument list from sets of positional and keyword
        arguments.  Update the optional so_needed list for those arguments that
        refer to a scriptable object.
        """

        if so_needed is None:
            so_needed = []

        all_args = []

        for arg in args:
            s = ScriptManager.arg_as_string(arg, so_needed)
            all_args.append(s)

        for name, value in kwargs.items():
            s = ScriptManager.arg_as_string(value, so_needed)
            all_args.append('%s=%s' % (name, s))

        return all_args

    @staticmethod
    def arg_as_string(arg, so_needed):
        """ Return the string representation of an argument.  Update the
        so_needed list if the argument refers to a scriptable object.  Any
        delayed conversion exception is handled here.
        """

        if isinstance(arg, Exception):
            raise arg

        if isinstance(arg, _ScriptObject):
            # Check it hasn't been unbound.
            if not arg.name:
                raise NameError("%s has been unbound but is needed by the script" % arg.obj_ref())

            # Add it to the needed list if it isn't already there.
            if arg not in so_needed:
                so_needed.append(arg)

            arg = arg.name

        return arg

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _new_method(self, func, args, kwargs):
        """ Return an object that encapsulates a call to a scriptable method.
        _add_method() must be called to add it to the current script.
        """

        # Convert each argument to its string representation if possible.
        # Doing this now avoids problems with mutable arguments.
        nargs = [self._object_as_string(arg) for arg in args]

        if type(func) is types.FunctionType:
            so = None
        else:
            so = nargs[0]
            nargs = nargs[1:]

        nkwargs = {}
        for name, value in kwargs.items():
            nkwargs[name] = self._object_as_string(value)

        return _ScriptMethod(name=func.__name__, so=so, args=nargs,
                kwargs=nkwargs)

    def _add_method(self, entry, result):
        """ Add a method call (returned by _new_method()), with it's associated
        result and ID, to the current script.
        """

        self._start_script()

        if result is not None:
            # Assume that a tuple represents multiple returned values - not
            # necessarily a valid assumption unless we make it a rule for
            # scriptable functions.
            if type(result) is type(()):
                for r in result:
                    self._save_result(r)
            else:
                self._save_result(result)

            entry.result = result

        self._calls.append(entry)

    def _add_trait_get(self, obj, name, result):
        """ Add a call to a trait getter, with it's associated result and ID,
        to the current script.  Return True if the get had side effects.
        """

        self._start_script()

        side_effects = obj.trait(name).has_side_effects

        if side_effects is None:
            side_effects = False

        so = self._object_as_string(obj)

        if result is not None:
            self._save_result(result)

        self._calls.append(_ScriptTraitGet(so=so, name=name, result=result,
                has_side_effects=side_effects))

        return side_effects

    def _add_trait_set(self, obj, name, value):
        """ Add a call to a trait setter, with it's associated value and ID,
        to the current script.
        """

        self._start_script()

        so = self._object_as_string(obj)
        value = self._object_as_string(value)

        self._calls.append(_ScriptTraitSet(so=so, name=name, value=value))

    def _unique_name(self, name, bind_policy):
        """ Return a name that is guaranteed to be unique according to the bind
        policy.
        """

        # See if the name is already is use.
        bo = self._namespace.get(name)

        if bo is None:
            self._names[name] = 1
        elif bind_policy == 'auto':
            suff = self._names[name]
            self._names[name] = suff + 1

            name = '%s%d' % (name, suff)
        elif bind_policy == 'rebind':
            self._unbind(bo)
        else:
            raise NameError("\"%s\" is already bound to a scriptable object" % name)

        return name

    def _unbind(self, bo):
        """Unbind the given bound object."""

        # Tell everybody it is no longer bound.  Don't bother if it is a
        # factory because the corresponding bound event wouldn't have been
        # fired.
        if not isinstance(bo, _FactoryObject):
            self.bind_event = BindEvent(name=bo.name, obj=None)

        # Forget about it.
        del self._namespace[bo.name]
        bo.name = ''

    @staticmethod
    def _gc_script_obj(obj_ref):
        """ The callback invoked when a scriptable object is garbage collected.
        """

        # Avoid recursive imports.
        from .package_globals import get_script_manager

        sm = get_script_manager()
        so = sm._so_by_ref[obj_ref]

        if so.name:
            sm._unbind(so)

        del sm._so_by_id[so.obj_id]
        del sm._so_by_ref[so.obj_ref]

    def _start_script(self):
        """ Save when a script recording is started. """

        if len(self._calls) == 0:
            self._when_started = datetime.datetime.now().strftime('%c')

    def _object_as_string(self, obj):
        """ Convert an object to a string as it will appear in a script.  An
        exception may be returned (not raised) if there was an error in the
        conversion.
        """

        obj_id = id(obj)

        # See if the argument is the result of a previous call.
        nr, _ = self._results.get(obj_id, (None, None))

        if nr is not None:
            if nr < 0:
                nr = self._next_result_nr
                self._next_result_nr += 1

                # Key on the ID of the argument (which is hashable) rather than
                # the argument itself (which might not be).
                self._results[obj_id] = (nr, obj)

            return "r%d" % nr

        return self._scriptable_object_as_string(obj)

    def _scriptable_object_as_string(self, obj):
        """ Convert an object to a string as it will appear in a script.  An
        exception may be returned (not raised) if there was an error in the
        conversion.
        """

        obj_id = id(obj)

        # If it is a scriptable object we return the object and convert it to a
        # string later when we know it is really needed.
        so = self._so_by_id.get(obj_id)

        if so is not None:
            return so

        # Use the repr result if it doesn't appear to be the generic response,
        # ie. it doesn't contain its own address as a hex string.
        s = repr(obj)

        if hex(obj_id) not in s:
            return s

        # We don't know how to represent the argument as a string.  This is
        # most likely because an appropriate __init__ hasn't been made
        # scriptable.  We don't raise an exception until the user decides to
        # convert the calls to a script.
        return ValueError("unable to create a script representation of %s" % obj)

    def _save_result(self, result):
        """ Save the result of a call to a scriptable method so that it can be
        recognised later.
        """

        if id(result) not in self._results:
            self._results[id(result)] = (-1, result)

    def _get_script(self):
        """ Convert the current list of calls to a script. """

        # Handle the trivial case.
        if len(self._calls) == 0:
            return ""

        # Generate the header.
        header = "# Script generated %s" % self._when_started

        # Generate the calls.
        so_needed = []
        calls = []

        for call in self._calls:
            s = call.as_str(self, so_needed)

            if s:
                calls.append(s)

        calls = "\n".join(calls)

        # Generate the scriptable object constructors.
        types_needed = []
        ctors = []

        for so in so_needed:
            if so.explicitly_bound:
                continue

            so_type = so.scripted_type
            args = self.args_as_string_list(so.args, so.kwargs)

            ctors.append("%s = %s(%s)" % (so.name, so_type.__name__, ", ".join(args)))

            # See if a new import is needed.
            if so_type not in types_needed:
                types_needed.append(so_type)

        ctors = "\n".join(ctors)

        # Generate the import statements.
        imports = []

        for so_type in types_needed:
            imports.append("from %s import %s" % (so_type.__module__, so_type.__name__))

        imports = "\n".join(imports)

        return "\n\n".join([header, imports, ctors, calls]) + "\n"
