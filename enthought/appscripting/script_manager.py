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
import weakref

# Enthought library imports.
from enthought.traits.api import Any, Bool, Dict, Event, HasTraits, \
        implements, Instance, Int, List, Property, Str, Unicode

# Local imports.
from i_script_manager import IScriptManager


class _ScriptInit(HasTraits):
    """ The _ScriptInit class encapsulates a single call to a scriptable
    object's __init__ method.
    """

    #### '_ScriptInit' interface ##############################################

    # The positional arguments passed to __init__ after being converted to
    # strings.  A particular argument may be an exception if it couldn't be
    # converted.
    args = List

    # The keyword arguments passed to __init__ after being converted to
    # strings.  A particular argument may be an exception if it couldn't be
    # converted.
    kwargs = Dict

    # The name the object will be bound to.
    name = Str

    # The number that will make the name unique.
    name_nr = Int(0)

    # A weak reference to the object.
    obj = Any

    # The type of the scriptable object.
    scripted_type = Any

    ###########################################################################
    # '_ScriptInit' interface.
    ###########################################################################

    def unique_name(self):
        """ Return the unique name that the object is bound to. """

        name = self.name
        if self.name_nr > 0:
            name += str(self.name_nr)

        return name


class _ScriptCall(HasTraits):
    """ The _ScriptCall class is the base class for all script calls. """

    #### '_ScriptCall' interface ##############################################

    # The name of the call.
    name = Str

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

    # The scriptable object containing the trait.
    so = Any

    ###########################################################################
    # '_ScriptCall' interface.
    ###########################################################################

    def as_str(self, sm, so_needed):
        """ Return the string equivalent of the call, updated the list of
        needed scriptable objects if required.
        """

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

        so = ScriptManager.arg_as_string(self.so, so_needed)

        return "%s%s.%s" % (rstr, so, self.name)


class _ScriptTraitSet(_ScriptCall):
    """ The _ScriptTraitSet class encapsulates a single call to the set of a
    scriptable trait.
    """

    #### '_ScriptTraitSet' interface ##########################################

    # The value the trait is set to.
    value = Any

    # The scriptable object containing the trait.
    so = Any

    ###########################################################################
    # '_ScriptCall' interface.
    ###########################################################################

    def as_str(self, sm, so_needed):
        """ Return the string equivalent of the call, updated the list of
        needed scriptable objects if required.
        """

        so = ScriptManager.arg_as_string(self.so, so_needed)
        value = ScriptManager.arg_as_string(self.value, so_needed)

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

        args = ScriptManager.args_as_string_list(self.args, self.kwargs, so_needed)

        return "%s%s.%s(%s)" % (rstr, args[0], self.name, ", ".join(args[1:]))


class ScriptManager(HasTraits):
    """ The ScriptManager class is the default implementation of
    IScriptManager.
    """

    implements(IScriptManager)

    #### 'IScriptManager' interface ###########################################

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

    # The next sequential result number.
    _next_result_nr = Int

    # The results returned by previous scriptable calls.  The key is the id()
    # of the result object.  The value is a two element tuple of the sequential
    # result number (easier for the user to use than the id()) and the result
    # object itself.
    _results = Dict

    # The dictionary of _ScriptInit instances keyed by the object's id().
    _scriptable_objects = Dict

    # The date and time when the script was recorded.
    _when_started = Any

    ###########################################################################
    # 'IScriptManager' interface.
    ###########################################################################

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

    def record_trait_get(self, so, name, result):
        """ Record the get of a trait of a scriptable object.  This is intended
        to be used only by the Scriptable trait getter.
        """

        if self.recording:
            side_effects = self._add_trait_get(so, name, result)

            # Don't needlessly fire the event if there are no side effects.
            if side_effects:
                self.script_updated = self

    def record_trait_set(self, so, name, value):
        """ Record the set of a trait of a scriptable object.  This is intended
        to be used only by the Scriptable trait getter.
        """

        if self.recording:
            self._add_trait_set(so, name, value)

            self.script_updated = self

    def new_object(self, obj, scripted_type, args, kwargs, name=None):
        """ Register a scriptable object and the arguments used to create it.
        """

        obj_id = id(obj)

        # See if we already know about the object.  This can happen if the
        # object had a decorated __init__ method so it would get registered by
        # the decorator and ScriptableObject.__init__.  The former would happen
        # first and would have a complete set of arguments.  Therefore, if we
        # do already know about it we don't do anything more.
        if not self._scriptable_objects.has_key(obj_id):
            # Convert each argument to its string representation if possible.
            # Doing this now avoids problems with mutable arguments.
            nargs = [self._scriptable_object_as_string(a) for a in args]

            nkwargs = {}
            for n, value in kwargs.iteritems():
                nkwargs[n] = self._scriptable_object_as_string(value)

            # The name defaults to the type name.
            if not name:
                name = scripted_type.__name__
                name = name[0].lower() + name[1:]

            obj_ref = weakref.ref(obj, self._gc_script_init)
            init = _ScriptInit(args=nargs, kwargs=nkwargs, name=name,
                    obj=obj_ref, scripted_type=scripted_type)
            self._scriptable_objects[obj_id] = init

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

        for name, value in kwargs.iteritems():
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

        if isinstance(arg, _ScriptInit):
            # Add it to the needed list if it isn't already there and generate
            # a named based on the type and how many of the type already exist.
            name_count = 0

            for so in so_needed:
                if so is arg:
                    break

                if so.name == arg.name:
                    name_count += 1
            else:
                so_needed.append(arg)
                arg.name_nr = name_count

            arg = arg.unique_name()

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

        nkwargs = {}
        for name, value in kwargs.iteritems():
            nkwargs[name] = self._object_as_string(value)

        return _ScriptMethod(name=func.func_name, args=nargs, kwargs=nkwargs)

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

    def _add_trait_get(self, so, name, result):
        """ Add a call to a trait getter, with it's associated result and ID,
        to the current script.  Return True if the get had side effects.
        """

        self._start_script()

        side_effects = so.trait(name).has_side_effects

        if side_effects is None:
            side_effects = False

        so = self._object_as_string(so)

        if result is not None:
            self._save_result(result)

        self._calls.append(_ScriptTraitGet(so=so, name=name, result=result,
                has_side_effects=side_effects))

        return side_effects

    def _add_trait_set(self, so, name, value):
        """ Add a call to a trait setter, with it's associated value and ID,
        to the current script.
        """

        self._start_script()

        so = self._object_as_string(so)
        value = self._object_as_string(value)

        self._calls.append(_ScriptTraitSet(so=so, name=name, value=value))

    @staticmethod
    def _gc_script_init(obj):
        """ The callback invoked when a scriptable object is garbage collected.
        """

        # Avoid recursive imports.
        from package_globals import get_script_manager

        get_script_manager()._scriptable_objects.pop(id(obj), None)

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
        so = self._scriptable_objects.get(obj_id)

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
            so_type = so.scripted_type
            args = ScriptManager.args_as_string_list(so.args, so.kwargs)

            ctors.append("    %s = %s(%s)" % (so.unique_name(), so_type.__name__, ", ".join(args)))

            # See if a new import is needed.
            if so_type not in types_needed:
                types_needed.append(so_type)

        ctors = "\n".join(ctors)

        # Generate the import statements.
        imports = []

        for so_type in types_needed:
            imports.append("    from %s import %s" % (so_type.__module__, so_type.__name__))

        if imports:
            imports.insert(0, "if __name__ == '__main__':")

        imports = "\n".join(imports)

        return "\n\n".join([header, imports, ctors, calls]) + "\n"
