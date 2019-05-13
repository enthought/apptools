"""This module provides code that allows one to pickle the state of a
Python object to a dictionary.

The motivation for this is simple.  The standard Python
pickler/unpickler is best used to pickle simple objects and does not
work too well for complex code.  Specifically, there are two major
problems (1) the pickle file format is not easy to edit with a text
editor and (2) when a pickle is unpickled, it creates all the
necessary objects and sets the state of these objects.

Issue (2) might not appear to be a problem.  However, often, the
determination of the entire 'state' of an application requires the
knowledge of the state of many objects that are not really in the
users concern.  The user would ideally like to pickle just what he
thinks is relevant.  Now, given that the user is not going to save the
entire state of the application, the use of pickle is insufficient
since the state is no longer completely known (or worth knowing).  The
default `Unpickler` recreates the objects and the typical
implementation of `__setstate__` is usually to simply update the
object's `__dict__` attribute.  This is inadequate because the pickled
information is taken out of the real context when it was saved.

The `StatePickler` basically pickles the 'state' of an object into a
large dictionary.  This pickled data may be easily unpickled and
modified on the interpreter or edited with a text editor
(`pprint.saferepr` is a friend).  The second problem is also
eliminated.  When this state is unpickled using `StateUnpickler`, what
you get is a special dictionary (a `State` instance).  This allows one
to navigate the state just like the original object.  Its up to the
user to create any new objects and set their states using this
information.  This allows for a lot of flexibility while allowing one
to save and set the state of (almost) any Python object.

The `StateSetter` class helps set the state of a known instance.  When
setting the state of an instance it checks to see if there is a
`__set_pure_state__` method that in turn calls `StateSetter.set`
appropriately.

Additionally, there is support for versioning.  The class' version is
obtain from the `__version__` class attribute.  This version along
with the versions of the bases of a class is embedded into the
metadata of the state and stored.  By using `version_registry.py` a
user may register a handler for a particular class and module.  When
the state of an object is set using `StateSetter.set_state`, then
these handlers are called in reverse order of their MRO.  This gives
the handler an opportunity to upgrade the state depending on its
version.  Builtin classes are not scanned for versions.  If a class
has no version, then by default it is assumed to be -1.


Example::

  >>> class A:
  ...    def __init__(self):
  ...        self.a = 'a'
  ...
  >>> a = A()
  >>> a.a = 100
  >>> import state_pickler
  >>> s = state_pickler.dumps(a)               # Dump the state of `a`.
  >>> state = state_pickler.loads_state(s)     # Get the state back.
  >>> b = state_pickler.create_instance(state) # Create the object.
  >>> state_pickler.set_state(b, state)        # Set the object's state.
  >>> assert b.a == 100


Features
--------

 - The output is a plain old dictionary so is easy to parse, edit etc.
 - Handles references to avoid duplication.
 - Gzips Numeric arrays when dumping them.
 - Support for versioning.


Caveats
-------

 - Does not pickle a whole bunch of stuff including code objects and
   functions.
 - The output is a pure dictionary and does not contain instances.  So
   using this *as it is* in `__setstate__` will not work.  Instead
   define a `__set_pure_state__` and use the `StateSetter` class or
   the `set_state` function provided by this module.


Notes
-----

  Browsing the code from XMarshaL_ and pickle.py proved useful for
  ideas.  None of the code is taken from there though.

.. _XMarshaL:  http://www.dezentral.de/soft/XMarshaL

"""
# Author: Prabhu Ramachandran <prabhu_r@users.sf.net>
# Copyright (c) 2005-2015, Enthought, Inc.
# License: BSD Style.

# Standard library imports.
import base64
import sys
import types
import pickle
import gzip
from io import BytesIO, StringIO

import numpy

# Local imports.
from . import version_registry
from .file_path import FilePath

PY_VER = sys.version_info[0]
NumpyArrayType = type(numpy.array([]))


def gzip_string(data):
    """Given a string (`data`) this gzips the string and returns it.
    """
    s = BytesIO()
    writer = gzip.GzipFile(mode='wb', fileobj=s)
    writer.write(data)
    writer.close()
    s.seek(0)
    return s.read()


def gunzip_string(data):
    """Given a gzipped string (`data`) this unzips the string and
    returns it.
    """
    if PY_VER== 2 or (bytes is not str and type(data) is bytes):
        s = BytesIO(data)
    else:
        s = StringIO(data)
    writer = gzip.GzipFile(mode='rb', fileobj=s)
    data = writer.read()
    writer.close()
    return data

class StatePicklerError(Exception):
    pass

class StateUnpicklerError(Exception):
    pass

class StateSetterError(Exception):
    pass

######################################################################
# `State` class
######################################################################
class State(dict):
    """Used to encapsulate the state of an instance in a very
    convenient form.  The '__metadata__' attribute/key is a dictionary
    that has class specific details like the class name, module name
    etc.
    """
    def __init__(self, **kw):
        dict.__init__(self, **kw)
        self.__dict__ = self

######################################################################
# `StateDict` class
######################################################################
class StateDict(dict):
    """Used to encapsulate a dictionary stored in a `State` instance.
    The has_instance attribute specifies if the dict has an instance
    embedded in it.
    """
    def __init__(self, **kw):
        dict.__init__(self, **kw)
        self.has_instance = False

######################################################################
# `StateList` class
######################################################################
class StateList(list):
    """Used to encapsulate a list stored in a `State` instance.  The
    has_instance attribute specifies if the list has an instance
    embedded in it.
    """
    def __init__(self, seq=None):
        if seq:
            list.__init__(self, seq)
        else:
            list.__init__(self)
        self.has_instance = False

######################################################################
# `StateTuple` class
######################################################################
class StateTuple(tuple):
    """Used to encapsulate a tuple stored in a `State` instance.  The
    has_instance attribute specifies if the tuple has an instance
    embedded in it.
    """
    def __new__(cls, seq=None):
        if seq:
            obj = super(StateTuple, cls).__new__(cls, tuple(seq))
        else:
            obj = super(StateTuple, cls).__new__(cls)
        obj.has_instance = False
        return obj


######################################################################
# `StatePickler` class
######################################################################
class StatePickler:
    """Pickles the state of an object into a dictionary.  The
    dictionary is itself either saved as a pickled file (`dump`) or
    pickled string (`dumps`).  Alternatively, the `dump_state` method
    will return the dictionary that is pickled.

    The format of the state dict is quite strightfoward.  Basic types
    (bool, int, long, float, complex, None, string and unicode) are
    represented as they are.  Everything else is stored as a
    dictionary containing metadata information on the object's type
    etc. and also the actual object in the 'data' key.  For example::

        >>> p = StatePickler()
        >>> p.dump_state(1)
        1
        >>> l = [1,2.0, None, [1,2,3]]
        >>> p.dump_state(l)
        {'data': [1, 2.0, None, {'data': [1, 2, 3], 'type': 'list', 'id': 1}],
         'id': 0,
         'type': 'list'}

    Classes are also represented similarly.  The state in this case is
    obtained from the `__getstate__` method or from the `__dict__`.
    Here is an example::

        >>> class A:
        ...     __version__ = 1  # State version
        ...     def __init__(self):
        ...         self.attribute = 1
        ...
        >>> a = A()
        >>> p = StatePickler()
        >>> p.dump_state(a)
        {'class_name': 'A',
         'data': {'data': {'attribute': 1}, 'type': 'dict', 'id': 2},
         'id': 0,
         'initargs': {'data': (), 'type': 'tuple', 'id': 1},
         'module': '__main__',
         'type': 'instance',
         'version': [(('A', '__main__'), 1)]}

    When pickling data, references are taken care of.  Numeric arrays
    can be pickled and are stored as a gzipped base64 encoded string.

    """
    def __init__(self):
        self._clear()
        type_map = {bool: self._do_basic_type,
                    complex: self._do_basic_type,
                    float: self._do_basic_type,
                    int: self._do_basic_type,
                    type(None): self._do_basic_type,
                    str: self._do_basic_type,
                    bytes: self._do_basic_type,
                    tuple: self._do_tuple,
                    list: self._do_list,
                    dict: self._do_dict,
                    NumpyArrayType: self._do_numeric,
                    State: self._do_state,
                    }
        if PY_VER == 2:
            type_map[long] = self._do_basic_type
            type_map[unicode] = self._do_basic_type
        self.type_map = type_map

    def dump(self, value, file):
        """Pickles the state of the object (`value`) into the passed
        file.
        """
        try:
            # Store the file name we are writing to so we can munge
            # file paths suitably.
            self.file_name = file.name
        except AttributeError:
            pass
        pickle.dump(self._do(value), file)

    def dumps(self, value):
        """Pickles the state of the object (`value`) and returns a
        string.
        """
        return pickle.dumps(self._do(value))

    def dump_state(self, value):
        """Returns a dictionary or a basic type representing the
        complete state of the object (`value`).

        This value is pickled by the `dump` and `dumps` methods.
        """
        return self._do(value)

    ######################################################################
    # Non-public methods
    ######################################################################
    def _clear(self):
        # Stores the file name of the file being used to dump the
        # state.  This is used to change any embedded paths relative
        # to the saved file.
        self.file_name = ''
        # Caches id's to handle references.
        self.obj_cache = {}
        # Misc cache to cache things that are not persistent.  For
        # example, object.__getstate__()/__getinitargs__() usually
        # returns a copy of a dict/tuple that could possibly be reused
        # on another object's __getstate__.  Caching these prevents
        # some wierd problems with the `id` of the object.
        self._misc_cache = []

    def _flush_traits(self, obj):
        """Checks if the object has traits and ensures that the traits
        are set in the `__dict__` so we can pickle it.
        """
        # Not needed with Traits3.
        return

    def _do(self, obj):
        obj_type = type(obj)
        key = self._get_id(obj)
        if key in self.obj_cache:
            return self._do_reference(obj)
        elif obj_type in self.type_map:
            return self.type_map[obj_type](obj)
        elif isinstance(obj, tuple):
            # Takes care of StateTuples.
            return self._do_tuple(obj)
        elif isinstance(obj, list):
            # Takes care of TraitListObjects.
            return self._do_list(obj)
        elif isinstance(obj, dict):
            # Takes care of TraitDictObjects.
            return self._do_dict(obj)
        elif hasattr(obj, '__dict__'):
            return self._do_instance(obj)

    def _get_id(self, value):
        try:
            key = hash(value)
        except TypeError:
            key = id(value)
        return key

    def _register(self, value):
        key = self._get_id(value)
        cache = self.obj_cache
        idx = len(cache)
        cache[key] = idx
        return idx

    def _do_basic_type(self, value):
        return value

    def _do_reference(self, value):
        key = self._get_id(value)
        idx = self.obj_cache[key]
        return dict(type='reference', id=idx, data=None)

    def _do_instance(self, value):
        # Flush out the traits.
        self._flush_traits(value)

        # Setup the relative paths of FilePaths before dumping.
        if self.file_name and isinstance(value, FilePath):
            value.set_relative(self.file_name)

        # Get the initargs.
        args = ()
        if hasattr(value, '__getinitargs__') and value.__getinitargs__:
            args = value.__getinitargs__()

        # Get the object state.
        if hasattr(value, '__get_pure_state__'):
            state = value.__get_pure_state__()
        elif hasattr(value, '__getstate__'):
            state = value.__getstate__()
        else:
            state = value.__dict__

        state.pop('__traits_version__', None)

        # Cache the args and state since they are likely to be gc'd.
        self._misc_cache.extend([args, state])
        # Register and process.
        idx = self._register(value)
        args_data = self._do(args)
        data = self._do(state)

        # Get the version of the object.
        version = version_registry.get_version(value)
        module = value.__class__.__module__
        class_name = value.__class__.__name__

        return dict(type='instance',
                    module=module,
                    class_name=class_name,
                    version=version,
                    id=idx,
                    initargs=args_data,
                    data=data)

    def _do_state(self, value):
        metadata = value.__metadata__
        args = metadata.get('initargs')
        state = dict(value)
        state.pop('__metadata__')

        self._misc_cache.extend([args, state])

        idx = self._register(value)
        args_data = self._do(args)
        data = self._do(state)

        return dict(type='instance',
                    module=metadata['module'],
                    class_name=metadata['class_name'],
                    version=metadata['version'],
                    id=idx,
                    initargs=args_data,
                    data=data)

    def _do_tuple(self, value):
        idx = self._register(value)
        data = tuple([self._do(x) for x in value])
        return dict(type='tuple', id=idx, data=data)

    def _do_list(self, value):
        idx = self._register(value)
        data = [self._do(x) for x in value]
        return dict(type='list', id=idx, data=data)

    def _do_dict(self, value):
        idx = self._register(value)
        vals = [self._do(x) for x in value.values()]
        data = dict(zip(value.keys(), vals))
        return dict(type='dict', id=idx, data=data)

    def _do_numeric(self, value):
        idx = self._register(value)
        if PY_VER > 2:
            data = base64.encodebytes(gzip_string(numpy.ndarray.dumps(value)))
        else:
            data = base64.encodestring(gzip_string(numpy.ndarray.dumps(value)))
        return dict(type='numeric', id=idx, data=data)



######################################################################
# `StateUnpickler` class
######################################################################
class StateUnpickler:
    """Unpickles the state of an object saved using StatePickler.

    Please note that unlike the standard Unpickler, no instances of
    any user class are created.  The data for the state is obtained
    from the file or string, reference objects are setup to refer to
    the same state value and this state is returned in the form
    usually in the form of a dictionary.  For example::

        >>> class A:
        ...     def __init__(self):
        ...         self.attribute = 1
        ...
        >>> a = A()
        >>> p = StatePickler()
        >>> s = p.dumps(a)
        >>> up = StateUnpickler()
        >>> state = up.loads_state(s)
        >>> state.__class__.__name__
        'State'
        >>> state.attribute
        1
        >>> state.__metadata__
        {'class_name': 'A',
         'has_instance': True,
         'id': 0,
         'initargs': (),
         'module': '__main__',
         'type': 'instance',
         'version': [(('A', '__main__'), -1)]}

    Note that the state is actually a `State` instance and is
    navigable just like the original object.  The details of the
    instance are stored in the `__metadata__` attribute.  This is
    highly convenient since it is possible for someone to view and
    modify the state very easily.
    """

    def __init__(self):
        self._clear()
        self.type_map = {'reference': self._do_reference,
                         'instance': self._do_instance,
                         'tuple': self._do_tuple,
                         'list': self._do_list,
                         'dict': self._do_dict,
                         'numeric': self._do_numeric,
                         }

    def load_state(self, file):
        """Returns the state of an object loaded from the pickled data
        in the given file.
        """
        try:
            self.file_name = file.name
        except AttributeError:
            pass
        data = pickle.load(file)
        result = self._process(data)
        return result

    def loads_state(self, string):
        """Returns the state of an object loaded from the pickled data
        in the given string.
        """
        data = pickle.loads(string)
        result = self._process(data)
        return result

    ######################################################################
    # Non-public methods
    ######################################################################
    def _clear(self):
        # The file from which we are being loaded.
        self.file_name = ''
        # Cache of the objects.
        self._obj_cache = {}
        # Paths to the instances.
        self._instances = []
        # Caches the references.
        self._refs = {}
        # Numeric arrays.
        self._numeric = {}

    def _set_has_instance(self, obj, value):
        if isinstance(obj, State):
            obj.__metadata__['has_instance'] = value
        elif isinstance(obj, (StateDict, StateList, StateTuple)):
            obj.has_instance = value

    def _process(self, data):
        result = self._do(data)

        # Setup all the Numeric arrays.  Do this first since
        # references use this.
        for key, (path, val) in self._numeric.items():
            if isinstance(result, StateTuple):
                result = list(result)
                exec('result%s = val'%path)
                result = StateTuple(result)
            else:
                exec('result%s = val'%path)

        # Setup the references so they really are references.
        for key, paths in self._refs.items():
            for path in paths:
                x = self._obj_cache[key]
                if isinstance(result, StateTuple):
                    result = list(result)
                    exec('result%s = x'%path)
                    result = StateTuple(result)
                else:
                    exec('result%s = x'%path)
                # if the reference is to an instance append its path.
                if isinstance(x, State):
                    self._instances.append(path)

        # Now setup the 'has_instance' attribute.  If 'has_instance'
        # is True then the object contains an instance somewhere
        # inside it.
        for path in self._instances:
            pth = path
            while pth:
                ns = {'result': result}
                exec('val = result%s'%pth, ns, ns)
                self._set_has_instance(ns['val'], True)
                end = pth.rfind('[')
                pth = pth[:end]
            # Now make sure that the first element also has_instance.
            self._set_has_instance(result, True)
        return result

    def _do(self, data, path=''):
        if type(data) is dict:
            return self.type_map[data['type']](data, path)
        else:
            return data

    def _do_reference(self, value, path):
        id = value['id']
        if id in self._refs:
            self._refs[id].append(path)
        else:
            self._refs[id] = [path]
        return State(__metadata__=value)

    def _handle_file_path(self, value):
        if (value['class_name'] == 'FilePath') and \
           ('file_path' in value['module']) and \
           self.file_name:
            data = value['data']['data']
            fp = FilePath(data['rel_pth'])
            fp.set_absolute(self.file_name)
            data['abs_pth'] = fp.abs_pth

    def _do_instance(self, value, path):
        self._instances.append(path)
        initargs = self._do(value['initargs'],
                            path + '.__metadata__["initargs"]')
        # Handle FilePaths.
        self._handle_file_path(value)

        d = self._do(value['data'], path)
        md = dict(type='instance',
                  module=value['module'],
                  class_name=value['class_name'],
                  version=value['version'],
                  id=value['id'],
                  initargs=initargs,
                  has_instance=True)
        result = State(**d)
        result.__metadata__ = md
        self._obj_cache[value['id']] = result
        return result

    def _do_tuple(self, value, path):
        res = []
        for i, x in enumerate(value['data']):
            res.append(self._do(x, path + '[%d]'%i))
        result = StateTuple(res)
        self._obj_cache[value['id']] = result
        return result

    def _do_list(self, value, path):
        result = StateList()
        for i, x in enumerate(value['data']):
            result.append(self._do(x, path + '[%d]'%i))
        self._obj_cache[value['id']] = result
        return result

    def _do_dict(self, value, path):
        result = StateDict()
        for key, val in value['data'].items():
            result[key] = self._do(val, path + '["%s"]'%key)
        self._obj_cache[value['id']] = result
        return result

    def _do_numeric(self, value, path):
        if PY_VER > 2:
            data = value['data']
            if isinstance(data, str):
                data = value['data'].encode('utf-8')
            junk = gunzip_string(base64.decodebytes(data))
            result = pickle.loads(junk, encoding='bytes')
        else:
            junk = gunzip_string(value['data'].decode('base64'))
            result = pickle.loads(junk)
        self._numeric[value['id']] = (path, result)
        self._obj_cache[value['id']] = result
        return result


######################################################################
# `StateSetter` class
######################################################################
class StateSetter:
    """This is a convenience class that helps a user set the
    attributes of an object given its saved state.  For instances it
    checks to see if a `__set_pure_state__` method exists and calls
    that when it sets the state.
    """
    def __init__(self):
        # Stores the ids of instances already done.
        self._instance_ids = []
        self.type_map = {State: self._do_instance,
                         StateTuple: self._do_tuple,
                         StateList: self._do_list,
                         StateDict: self._do_dict,
                         }

    def set(self, obj, state, ignore=None, first=None, last=None):
        """Sets the state of the object.

        This is to be used as a means to simplify loading the state of
        an object from its `__setstate__` method using the dictionary
        describing its state.  Note that before the state is set, the
        registered handlers for the particular class are called in
        order to upgrade the version of the state to the latest
        version.

        Parameters
        ----------

        - obj : `object`

          The object whose state is to be set.  If this is `None`
          (default) then the object is created.

        - state : `dict`

          The dictionary representing the state of the object.

        - ignore : `list(str)`

          The list of attributes specified in this list are ignored
          and the state of these attributes are not set (this excludes
          the ones specified in `first` and `last`).  If one specifies
          a '*' then all attributes are ignored except the ones
          specified in `first` and `last`.

        - first : `list(str)`

          The list of attributes specified in this list are set first (in
          order), before any other attributes are set.

        - last : `list(str)`

          The list of attributes specified in this list are set last (in
          order), after all other attributes are set.

        """
        if (not isinstance(state, State)) and \
               state.__metadata__['type'] != 'instance':
            raise StateSetterError(
                'Can only set the attributes of an instance.'
            )

        # Upgrade the state to the latest using the registry.
        self._update_and_check_state(obj, state)

        self._register(obj)

        # This wierdness is needed since the state's own `keys` might
        # be set to something else.
        state_keys = list(dict.keys(state))
        state_keys.remove('__metadata__')

        if first is None:
            first = []
        if last is None:
            last = []

        # Remove all the ignored keys.
        if ignore:
            if '*' in ignore:
                state_keys = first + last
            else:
                for name in ignore:
                    try:
                        state_keys.remove(name)
                    except KeyError:
                        pass

        # Do the `first` attributes.
        for key in first:
            state_keys.remove(key)
            self._do(obj, key, state[key])

        # Remove the `last` attributes.
        for key in last:
            state_keys.remove(key)

        # Set the remaining attributes.
        for key in state_keys:
            self._do(obj, key, state[key])

        # Do the last ones in order.
        for key in last:
            self._do(obj, key, state[key])

    ######################################################################
    # Non-public methods.
    ######################################################################
    def _register(self, obj):
        idx = id(obj)
        if idx not in self._instance_ids:
            self._instance_ids.append(idx)

    def _is_registered(self, obj):
        return (id(obj) in self._instance_ids)

    def _has_instance(self, value):
        """Given something (`value`) that is part of the state this
        returns if the value has an instance embedded in it or not.
        """
        if isinstance(value, State):
            return True
        elif isinstance(value, (StateDict, StateList, StateTuple)):
            return value.has_instance
        return False

    def _get_pure(self, value):
        """Returns the Python representation of the object (usually a
        list, tuple or dict) that has no instances embedded within it.
        """
        result = value
        if self._has_instance(value):
            raise StateSetterError(
                'Value has an instance: %s'%value
            )
        if isinstance(value, (StateList, StateTuple)):
            result = [self._get_pure(x) for x in value]
            if isinstance(value, StateTuple):
                result = tuple(result)
        elif isinstance(value, StateDict):
            result = {}
            for k, v in value.items():
                result[k] = self._get_pure(v)
        return result

    def _update_and_check_state(self, obj, state):
        """Updates the state from the registry and then checks if the
        object and state have same class.
        """
        # Upgrade this state object to the latest using the registry.
        # This is done before testing because updating may change the
        # class name/module.
        version_registry.registry.update(state)

        # Make sure object and state have the same class and module names.
        metadata = state.__metadata__
        cls = obj.__class__
        if (metadata['class_name'] != cls.__name__):
            raise StateSetterError(
                'Instance (%s) and state (%s) do not have the same class'\
                ' name!'%(cls.__name__, metadata['class_name'])
            )
        if (metadata['module'] != cls.__module__):
            raise StateSetterError(
                'Instance (%s) and state (%s) do not have the same module'\
                ' name!'%(cls.__module__, metadata['module'])
            )

    def _do(self, obj, key, value):
        try:
            attr = getattr(obj, key)
        except AttributeError:
            raise StateSetterError(
                'Object %s does not have an attribute called: %s'%(obj, key)
            )

        if isinstance(value, (State, StateDict, StateList, StateTuple)):
            # Special handlers are needed.
            if not self._has_instance(value):
                result = self._get_pure(value)
                setattr(obj, key, result)
            elif isinstance(value, StateTuple):
                setattr(obj, key, self._do_tuple(getattr(obj, key), value))
            else:
                self._do_object(getattr(obj, key), value)
        else:
            setattr(obj, key, value)

    def _do_object(self, obj, state):
        self.type_map[state.__class__](obj, state)

    def _do_instance(self, obj, state):
        if self._is_registered(obj):
            return
        else:
            self._register(obj)

        metadata = state.__metadata__
        if hasattr(obj, '__set_pure_state__'):
            self._update_and_check_state(obj, state)
            obj.__set_pure_state__(state)
        elif 'tvtk_classes' in metadata['module']:
            self._update_and_check_state(obj, state)
            tmp = self._get_pure(StateDict(**state))
            del tmp['__metadata__']
            obj.__setstate__(tmp)
        else:
            # No need to update or check since `set` does it for us.
            self.set(obj, state)

    def _do_tuple(self, obj, state):
        if not self._has_instance(state):
            return self._get_pure(state)
        else:
            result = list(obj)
            self._do_list(result, state)
            return tuple(result)

    def _do_list(self, obj, state):
        if len(obj) == len(state):
            for i in range(len(obj)):
                if not self._has_instance(state[i]):
                    obj[i] = self._get_pure(state[i])
                elif isinstance(state[i], tuple):
                    obj[i] = self._do_tuple(state[i])
                else:
                    self._do_object(obj[i], state[i])
        else:
            raise StateSetterError(
                'Cannot set state of list of incorrect size.'
            )

    def _do_dict(self, obj, state):
        for key, value in state.items():
            if not self._has_instance(value):
                obj[key] = self._get_pure(value)
            elif isinstance(value, tuple):
                obj[key] = self._do_tuple(value)
            else:
                self._do_object(obj[key], value)


######################################################################
# Internal Utility functions.
######################################################################
def _get_file_read(f):
    if hasattr(f, 'read'):
        return f
    else:
        return open(f, 'rb')

def _get_file_write(f):
    if hasattr(f, 'write'):
        return f
    else:
        return open(f, 'wb')


######################################################################
# Utility functions.
######################################################################
def dump(value, file):
    """Pickles the state of the object (`value`) into the passed file
    (or file name).
    """
    f = _get_file_write(file)
    try:
        StatePickler().dump(value, f)
    finally:
        f.flush()
        if f is not file:
            f.close()


def dumps(value):
    """Pickles the state of the object (`value`) and returns a string.
    """
    return StatePickler().dumps(value)


def load_state(file):
    """Returns the state of an object loaded from the pickled data in
    the given file (or file name).
    """
    f = _get_file_read(file)
    try:
        state = StateUnpickler().load_state(f)
    finally:
        if f is not file:
            f.close()
    return state


def loads_state(string):
    """Returns the state of an object loaded from the pickled data
    in the given string.
    """
    return StateUnpickler().loads_state(string)


def get_state(obj):
    """Returns the state of the object (usually as a dictionary).  The
    returned state may be used directy to set the state of the object
    via `set_state`.
    """
    s = dumps(obj)
    return loads_state(s)


def set_state(obj, state, ignore=None, first=None, last=None):
    StateSetter().set(obj, state, ignore, first, last)
set_state.__doc__ = StateSetter.set.__doc__


def update_state(state):
    """Given the state of an object, this updates the state to the
    latest version using the handlers given in the version registry.
    The state is modified in-place.
    """
    version_registry.registry.update(state)


def create_instance(state):
    """Create an instance from the state if possible.
    """
    if (not isinstance(state, State)) and \
           ('class_name'  not in state.__metadata__):
        raise StateSetterError('No class information in state')
    metadata = state.__metadata__
    class_name = metadata.get('class_name')
    mod_name = metadata.get('module')
    if 'tvtk_classes' in mod_name:
        # FIXME: This sort of special-case is probably indicative of something
        # that needs more thought, plus it makes it tought to decide whether
        # this component depends on tvtk!
        from tvtk.api import tvtk
        return getattr(tvtk, class_name)()

    initargs = metadata['initargs']
    if initargs.has_instance:
        raise StateUnpicklerError('Cannot unpickle non-trivial initargs')

    __import__(mod_name, globals(), locals(), class_name)
    mod = sys.modules[mod_name]
    cls = getattr(mod, class_name)
    return cls(*initargs)
