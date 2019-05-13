"""A special unpickler that gives you a state object and a special
pickler that lets you re-pickle that state.

The nice thing about creating state objects is that it does not import
any modules and does not create any instances.  Instead of instances
it creates `State` instances which have the same attributes as the
real object.  With this you can load a pickle (without even having the
modules on the machine), modify it and re-pickle it back.

NOTE: This module is not likely to work for very complex pickles but
 it should work for most common cases.

"""
# Author: Prabhu Ramachandran <prabhu@aero.iitb.ac.in>
# Copyright (c) 2006-2015, Prabhu Ramachandran
# License: BSD Style.

import sys
if sys.version_info[0] > 2:
    raise ImportError("This module does not work with Python 3.x")

import warnings
import pickle
import struct
from pickle import Pickler, Unpickler, dumps, BUILD, NEWOBJ, REDUCE, \
     MARK, OBJ, INST, BUILD, PicklingError, GLOBAL, \
     EXT1, EXT2, EXT4, _extension_registry, _keep_alive

from io import BytesIO


######################################################################
# `State` class
######################################################################
class State(dict):
    """Used to encapsulate the state of an instance in a very
    convenient form.  The '__METADATA__' attribute/key is a dictionary
    that has class specific details like the class name, module name
    etc.
    """
    def __init__(self, **kw):
        dict.__init__(self, **kw)
        self.__dict__ = self


######################################################################
# `StatePickler` class
######################################################################
class StatePickler(Pickler):
    """Pickles a `State` object back as a regular pickle that may be
    unpickled.
    """

    def __init__(self, file, protocol, bin=None):
        Pickler.__init__(self, file, protocol)
        self.bin = bin

    def save(self, obj):
        # Check the memo
        x = self.memo.get(id(obj))
        if x:
            self.write(self.get(x[0]))
            return

        if isinstance(obj, State):
            md = obj.__METADATA__
            typ = md['type']
            if typ == 'instance':
                self._state_instance(obj)
            elif typ in ['newobj', 'reduce']:
                self._state_reduce(obj)
            elif typ in ['class']:
                self._save_global(obj)
        else:
            Pickler.save(self, obj)

    def _state_instance(self, obj):
        md = obj.__METADATA__
        cls = md.get('class')
        cls_md = cls.__METADATA__

        memo  = self.memo
        write = self.write
        save  = self.save

        args = md.get('initargs')
        if len(args) > 0:
            _keep_alive(args, memo)

        write(MARK)

        if self.bin:
            save(cls)
            for arg in args:
                save(arg)
            write(OBJ)
        else:
            for arg in args:
                save(arg)
            write(INST + cls_md.get('module') + '\n' + cls_md.get('name') + '\n')

        self.memoize(obj)

        stuff = dict(obj.__dict__)
        stuff.pop('__METADATA__')

        if '__setstate_data__' in stuff:
            data = stuff.pop('__setstate_data__')
            _keep_alive(data, memo)
            save(data)
        else:
            save(stuff)
        write(BUILD)

    def _state_reduce(self, obj):
        # FIXME: this code is not as complete as pickle's reduce
        # handling code and is likely to not work in all cases.

        md = obj.__METADATA__
        func = md.get('class')
        func_md = func.__METADATA__
        args = md.get('initargs')
        state = dict(obj.__dict__)
        state.pop('__METADATA__')

        # This API is called by some subclasses

        # Assert that args is a tuple or None
        if not isinstance(args, tuple):
            if args is None:
                # A hack for Jim Fulton's ExtensionClass, now deprecated.
                # See load_reduce()
                warnings.warn("__basicnew__ special case is deprecated",
                              DeprecationWarning)
            else:
                raise PicklingError(
                    "args from reduce() should be a tuple")

        # Assert that func is callable
        #if not callable(func):
        #    raise PicklingError("func from reduce should be callable")

        save = self.save
        write = self.write

        # Protocol 2 special case: if func's name is __newobj__, use NEWOBJ
        if self.proto >= 2 and func_md.get("name", "") == "__newobj__":
            # FIXME: this is unlikely to work.
            cls = args[0]
            if not hasattr(cls, "__new__"):
                raise PicklingError(
                    "args[0] from __newobj__ args has no __new__")
            if obj is not None and cls is not obj.__class__:
                raise PicklingError(
                    "args[0] from __newobj__ args has the wrong class")
            args = args[1:]
            save(cls)
            save(args)
            write(NEWOBJ)
        else:
            save(func)
            save(args)
            write(REDUCE)

        if obj is not None:
            self.memoize(obj)

        if state is not None:
            if '__setstate_data__' in state:
                data = state.pop('__setstate_data__')
                save(data)
            else:
                save(state)
            write(BUILD)

    def _save_global(self, obj, name=None, pack=struct.pack):
        write = self.write
        memo = self.memo

        md = obj.__METADATA__

        if name is None:
            name = md.get('name')

        module = md.get('module')

        if self.proto >= 2:
            code = _extension_registry.get((module, name))
            if code:
                assert code > 0
                if code <= 0xff:
                    write(EXT1 + chr(code))
                elif code <= 0xffff:
                    write("%c%c%c" % (EXT2, code&0xff, code>>8))
                else:
                    write(EXT4 + pack("<i", code))
                return

        write(GLOBAL + module + '\n' + name + '\n')
        self.memoize(obj)


######################################################################
# `StateUnpickler` class
######################################################################
class StateUnpickler(Unpickler):
    def _instantiate(self, klass, k):
        args = tuple(self.stack[k+1:])
        del self.stack[k:]
        metadata = {'initargs': args, 'class': klass, 'type': 'instance'}
        value = State(__METADATA__=metadata)
        self.append(value)

    def load_build(self):
        stack = self.stack
        state = stack.pop()
        # Inst here is a State object.
        inst = stack[-1]
        slotstate = None
        if isinstance(state, tuple) and len(state) == 2:
            state, slotstate = state
        if state:
            if isinstance(state, tuple):
                inst.__dict__['__setstate_data__'] = state
            else:
                inst.__dict__.update(state)
        if slotstate:
            for k, v in slotstate.items():
                setattr(inst, k, v)
    Unpickler.dispatch[BUILD] = load_build

    def load_newobj(self):
        args = self.stack.pop()
        cls = self.stack[-1]
        cls_md = cls.__METADATA__
        metadata = {'initargs': args, 'class': cls, 'type': 'newobj'}
        obj = State(__METADATA__ = metadata)
        #obj = cls.__new__(cls, *args)
        self.stack[-1] = obj
    Unpickler.dispatch[NEWOBJ] = load_newobj

    def load_reduce(self):
        stack = self.stack
        args = stack.pop()
        func = stack[-1]
        func_md = func.__METADATA__
        metadata = {'initargs': args, 'class': func, 'type': 'reduce'}
        value = State(__METADATA__ = metadata)
        stack[-1] = value
    Unpickler.dispatch[REDUCE] = load_reduce

    def load(self):
        # We overload the load_build method so update the dispatch dict.
        dispatch = self.dispatch
        dispatch[BUILD] = StateUnpickler.load_build
        dispatch[NEWOBJ] = StateUnpickler.load_newobj
        dispatch[REDUCE] = StateUnpickler.load_reduce
        # call the super class' method.
        ret = Unpickler.load(self)
        # Reset the Unpickler's dispatch
        dispatch[BUILD] = Unpickler.load_build
        dispatch[NEWOBJ] = Unpickler.load_newobj
        dispatch[REDUCE] = Unpickler.load_reduce
        return ret

    def find_class(self, module, name):
        metadata = {'module': module, 'name': name, 'type': 'class'}
        value = State(__METADATA__ = metadata)
        return value


######################################################################
# Utility functions.
######################################################################
def get_state(obj):
    """Return a State object given an object.  Useful for testing."""
    str = dumps(obj)
    return StateUnpickler(BytesIO(str)).load()

def dump_state(state, file, protocol=None, bin=None):
    """Dump the state (potentially modified) to given file."""
    StatePickler(file, protocol, bin).dump(state)

def dumps_state(state, protocol=None, bin=None):
    """Dump the state (potentially modified) to a string and return
    the string."""
    file = BytesIO()
    StatePickler(file, protocol, bin).dump(state)
    return file.getvalue()

def state2object(state):
    """Creates an object from a state."""
    s = dumps_state(state)
    return pickle.loads(s)

def load_state(file):
    """Loads the state from a file like object.  This does not import
    any modules."""
    return StateUnpickler(file).load()

def loads_state(string):
    """Loads the state from a string object.  This does not import any
    modules."""
    return StateUnpickler(BytesIO(string)).load()
