# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


def get_mro(obj_class):
    """Get a reasonable method resolution order of a class and its
    superclasses for both old-style and new-style classes.
    """
    if not hasattr(obj_class, "__mro__"):
        # Old-style class. Mix in object to make a fake new-style class.
        try:
            obj_class = type(obj_class.__name__, (obj_class, object), {})
        except TypeError:
            # Old-style extension type that does not descend from object.
            mro = [obj_class]
        else:
            mro = obj_class.__mro__[1:-1]
    else:
        mro = obj_class.__mro__
    return mro


def _mod_name_key(typ):
    """Return a '__module__:__name__' key for a type."""
    module = getattr(typ, "__module__", None)
    name = getattr(typ, "__name__", None)
    key = "{0}:{1}".format(module, name)
    return key


class TypeRegistry(object):
    """Register objects for types.

    Each type maintains a stack of registered objects that can be pushed and
    popped.
    """

    def __init__(self):
        # Map types to lists of registered objects. The last is the most
        # current and will be the one that is returned on lookup.
        self.type_map = {}

        # Map '__module__:__name__' strings to lists of registered objects.
        self.name_map = {}

        # Map abstract base classes to lists of registered objects.
        self.abc_map = {}

    #### TypeRegistry public interface ########################################

    def push(self, typ, obj):
        """Push an object onto the stack for the given type.

        Parameters
        ----------
        typ : type or '__module__:__name__' string for a type
        obj : object
            The object to register.
        """
        if isinstance(typ, str):
            # Check the cached types.
            for cls in self.type_map:
                if _mod_name_key(cls) == typ:
                    self.type_map[cls].append(obj)
                    break
            else:
                if typ not in self.name_map:
                    self.name_map[typ] = []
                self.name_map[typ].append(obj)
        else:
            if typ not in self.type_map:
                self.type_map[typ] = []
            self.type_map[typ].append(obj)

    def push_abc(self, typ, obj):
        """Push an object onto the stack for the given ABC.

        Parameters
        ----------
        typ : abc.ABCMeta
        obj : object
        """
        if typ not in self.abc_map:
            self.abc_map[typ] = []
        self.abc_map[typ].append(obj)

    def pop(self, typ):
        """Pop a registered object for the given type.

        Parameters
        ----------
        typ : type or '__module__:__name__' string for a type

        Returns
        -------
        obj : object
            The last registered object for the type.

        Raises
        ------
        KeyError if the type is not registered.
        """
        if isinstance(typ, str):
            if typ not in self.name_map:
                # We may have it cached in the type map. We will have to
                # iterate over all of the types to check.
                for cls in self.type_map:
                    if _mod_name_key(cls) == typ:
                        old = self._pop_value(self.type_map, cls)
                        break
                else:
                    raise KeyError("No registered value for {0!r}".format(typ))
            else:
                old = self._pop_value(self.name_map, typ)
        else:
            if typ in self.type_map:
                old = self._pop_value(self.type_map, typ)
            elif typ in self.abc_map:
                old = self._pop_value(self.abc_map, typ)
            else:
                old = self._pop_value(self.name_map, _mod_name_key(typ))
        return old

    def lookup(self, instance):
        """Look up the registered object for the given instance.

        Parameters
        ----------
        instance : object
            An instance of a possibly registered type.

        Returns
        -------
        obj : object
            The registered object for the type of the instance, one of the
            type's superclasses, or else one of the ABCs the type implements.

        Raises
        ------
        KeyError if the instance's type has not been registered.
        """
        return self.lookup_by_type(type(instance))

    def lookup_by_type(self, typ):
        """Look up the registered object for a type.

        Parameters
        ----------
        typ  : type

        Returns
        -------
        obj : object
            The registered object for the type, one of its superclasses, or
            else one of the ABCs it implements.

        Raises
        ------
        KeyError if the type has not been registered.
        """
        return self.lookup_all_by_type(typ)[-1]

    def lookup_all(self, instance):
        """Look up all the registered objects for the given instance.

        Parameters
        ----------
        instance : object
            An instance of a possibly registered type.

        Returns
        -------
        objs : list of objects
            The list of registered objects for the instance. If the given
            instance is not registered, its superclasses are searched. If none
            of the superclasses are registered, search the possible ABCs.

        Raises
        ------
        KeyError if the instance's type has not been registered.
        """
        return self.lookup_all_by_type(type(instance))

    def lookup_all_by_type(self, typ):
        """Look up all the registered objects for a type.

        Parameters
        ----------
        typ  : type

        Returns
        -------
        objs : list of objects
            The list of registered objects for the type. If the given type is
            not registered, its superclasses are searched. If none of the
            superclasses are registered, search the possible ABCs.

        Raises
        ------
        KeyError if the type has not been registered.
        """
        # If a concrete superclass is registered use it.
        for cls in get_mro(typ):
            if cls in self.type_map or self._in_name_map(cls):
                objs = self.type_map[cls]
                if objs:
                    return objs

        # None of the concrete superclasses. Check the ABCs.
        for abstract, objs in self.abc_map.items():
            if issubclass(typ, abstract) and objs:
                return objs

        # If we have reached here, the lookup failed.
        raise KeyError("No registered value for {0!r}".format(typ))

    #### Private implementation ###############################################

    def _pop_value(self, mapping, key):
        """Pop a value from a keyed stack in a mapping, taking care to remove
        the key if the stack is depleted.
        """
        objs = mapping[key]
        old = objs.pop()
        if not objs:
            del mapping[key]
        return old

    def _in_name_map(self, typ):
        """Check if the given type is specified in the name map.

        Parameters
        ----------
        typ : type

        Returns
        -------
        is_in_name_map : bool
            If True, the registered value will be moved over to the type map
            for future lookups.
        """
        key = _mod_name_key(typ)
        if key in self.name_map:
            self.type_map[typ] = self.name_map.pop(key)
            return True
        else:
            return False


class LazyRegistry(TypeRegistry):
    """A type registry that will lazily import the registered objects.

    Register '__module__:__name__' strings for the lazily imported objects.
    These will only be imported when the matching type is looked up. The module
    name must be a fully-qualified absolute name with all of the parent
    packages specified.
    """

    def lookup_by_type(self, typ):
        """Look up the registered object for a type."""
        mod_name = TypeRegistry.lookup_by_type(self, typ)
        return self._import_object(mod_name)

    def _import_object(self, mod_object):
        module, name = mod_object.split(":")
        mod = __import__(module, {}, {}, [name], 0)
        return getattr(mod, name)
