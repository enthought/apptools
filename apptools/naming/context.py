# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" The base class for all naming contexts. """


# Enthought library imports.
from traits.api import Any, Dict, Event, HasTraits
from traits.api import Property, Str

# Local imports.
from .binding import Binding
from .exception import InvalidNameError, NameAlreadyBoundError
from .exception import NameNotFoundError, NotContextError
from .naming_event import NamingEvent
from .naming_manager import naming_manager
from .unique_name import make_unique_name


# Constants for environment property keys.
INITIAL_CONTEXT_FACTORY = "apptools.naming.factory.initial"
OBJECT_FACTORIES = "apptools.naming.factory.object"
STATE_FACTORIES = "apptools.naming.factory.state"


# The default environment.
ENVIRONMENT = {
    # 'Context' properties.
    OBJECT_FACTORIES: [],
    STATE_FACTORIES: [],
}


class Context(HasTraits):
    """ The base class for all naming contexts. """

    # Keys for environment properties.
    INITIAL_CONTEXT_FACTORY = INITIAL_CONTEXT_FACTORY
    OBJECT_FACTORIES = OBJECT_FACTORIES
    STATE_FACTORIES = STATE_FACTORIES

    #### 'Context' interface ##################################################

    # The naming environment in effect for this context.
    environment = Dict(ENVIRONMENT)

    # The name of the context within its own namespace.
    namespace_name = Property(Str)

    #### Events ####

    # Fired when an object has been added to the context (either via 'bind' or
    # 'create_subcontext').
    object_added = Event(NamingEvent)

    # Fired when an object has been changed (via 'rebind').
    object_changed = Event(NamingEvent)

    # Fired when an object has been removed from the context (either via
    # 'unbind' or 'destroy_subcontext').
    object_removed = Event(NamingEvent)

    # Fired when an object in the context has been renamed (via 'rename').
    object_renamed = Event(NamingEvent)

    # Fired when the contents of the context have changed dramatically.
    context_changed = Event(NamingEvent)

    #### Protected 'Context' interface #######################################

    # The bindings in the context.
    _bindings = Dict(Str, Any)

    ###########################################################################
    # 'Context' interface.
    ###########################################################################

    #### Properties ###########################################################

    def _get_namespace_name(self):
        """
        Return the name of the context within its own namespace.

        That is the full-path, through the namespace this context participates
        in, to get to this context.  For example, if the root context of the
        namespace was called 'Foo', and there was a subcontext of that called
        'Bar', and we were within that and called 'Baz', then this should
        return 'Foo/Bar/Baz'.

        """

        # FIXME: We'd like to raise an exception and force implementors to
        # decide what to do.  However, it appears to be pretty common that
        # most Context implementations do not override this method -- possibly
        # because the comments aren't clear on what this is supposed to be?
        #
        # Anyway, if we raise an exception then it is impossible to use any
        # evaluations when building a Traits UI for a Context.  That is, the
        # Traits UI can't include items that have a 'visible_when' or
        # 'enabled_when' evaluation.  This is because the Traits evaluation
        # code calls the 'get()' method on the Context which attempts to
        # retrieve the current namespace_name value.
        # raise OperationNotSupportedError()
        return ""

    #### Methods ##############################################################

    def bind(self, name, obj, make_contexts=False):
        """Binds a name to an object.

        If 'make_contexts' is True then any missing intermediate contexts are
        created automatically.

        """

        if len(name) == 0:
            raise InvalidNameError("empty name")

        # Parse the name.
        components = self._parse_name(name)

        # If there is exactly one component in the name then the operation
        # takes place in this context.
        if len(components) == 1:
            atom = components[0]

            # Is the name already bound?
            if self._is_bound(atom):
                raise NameAlreadyBoundError(name)

            # Do the actual bind.
            self._bind(atom, obj)

            # Trait event notification.
            self.object_added = NamingEvent(
                new_binding=Binding(name=name, obj=obj, context=self)
            )

        # Otherwise, attempt to continue resolution into the next context.
        else:
            if not self._is_bound(components[0]):
                if make_contexts:
                    self._create_subcontext(components[0])

                else:
                    raise NameNotFoundError(components[0])

            next_context = self._get_next_context(components[0])
            next_context.bind("/".join(components[1:]), obj, make_contexts)

    def rebind(self, name, obj, make_contexts=False):
        """Binds an object to a name that may already be bound.

        If 'make_contexts' is True then any missing intermediate contexts are
        created automatically.

        The object may be a different object but may also be the same object
        that is already bound to the specified name. The name may or may not be
        already used. Think of this as a safer version of 'bind' since this
        one will never raise an exception regarding a name being used.

        """

        if len(name) == 0:
            raise InvalidNameError("empty name")

        # Parse the name.
        components = self._parse_name(name)

        # If there is exactly one component in the name then the operation
        # takes place in this context.
        if len(components) == 1:
            # Do the actual rebind.
            self._rebind(components[0], obj)

            # Trait event notification.
            self.object_changed = NamingEvent(
                new_binding=Binding(name=name, obj=obj, context=self)
            )

        # Otherwise, attempt to continue resolution into the next context.
        else:
            if not self._is_bound(components[0]):
                if make_contexts:
                    self._create_subcontext(components[0])

                else:
                    raise NameNotFoundError(components[0])

            next_context = self._get_next_context(components[0])
            next_context.rebind("/".join(components[1:]), obj, make_contexts)

    def unbind(self, name):
        """ Unbinds a name. """

        if len(name) == 0:
            raise InvalidNameError("empty name")

        # Parse the name.
        components = self._parse_name(name)

        # If there is exactly one component in the name then the operation
        # takes place in this context.
        if len(components) == 1:
            atom = components[0]

            if not self._is_bound(atom):
                raise NameNotFoundError(name)

            # Lookup the object that we are unbinding to use in the event
            # notification.
            obj = self._lookup(atom)

            # Do the actual unbind.
            self._unbind(atom)

            # Trait event notification.
            self.object_removed = NamingEvent(
                old_binding=Binding(name=name, obj=obj, context=self)
            )

        # Otherwise, attempt to continue resolution into the next context.
        else:
            if not self._is_bound(components[0]):
                raise NameNotFoundError(components[0])

            next_context = self._get_next_context(components[0])
            next_context.unbind("/".join(components[1:]))

    def rename(self, old_name, new_name):
        """ Binds a new name to an object. """

        if len(old_name) == 0 or len(new_name) == 0:
            raise InvalidNameError("empty name")

        # Parse the names.
        old_components = self._parse_name(old_name)
        new_components = self._parse_name(new_name)

        # If there is axactly one component in BOTH names then the operation
        # takes place ENTIRELY in this context.
        if len(old_components) == 1 and len(new_components) == 1:
            # Is the old name actually bound?
            if not self._is_bound(old_name):
                raise NameNotFoundError(old_name)

            # Is the new name already bound?
            if self._is_bound(new_name):
                raise NameAlreadyBoundError(new_name)

            # Do the actual rename.
            self._rename(old_name, new_name)

            # Lookup the object that we are renaming to use in the event
            # notification.
            obj = self._lookup(new_name)

            # Trait event notification.
            self.object_renamed = NamingEvent(
                old_binding=Binding(name=old_name, obj=obj, context=self),
                new_binding=Binding(name=new_name, obj=obj, context=self),
            )

        else:
            # fixme: This really needs to be transactional in case the bind
            # succeeds but the unbind fails.  To be safe should we just not
            # support cross-context renaming for now?!?!
            #
            # Lookup the object.
            obj = self.lookup(old_name)

            # Bind the new name.
            self.bind(new_name, obj)

            # Unbind the old one.
            self.unbind(old_name)

    def lookup(self, name):
        """ Resolves a name relative to this context. """

        # If the name is empty we return the context itself.
        if len(name) == 0:
            # fixme: The JNDI spec. says that this should return a COPY of
            # the context.
            return self

        # Parse the name.
        components = self._parse_name(name)

        # If there is exactly one component in the name then the operation
        # takes place in this context.
        if len(components) == 1:
            atom = components[0]

            if not self._is_bound(atom):
                raise NameNotFoundError(name)

            # Do the actual lookup.
            obj = self._lookup(atom)

        # Otherwise, attempt to continue resolution into the next context.
        else:
            if not self._is_bound(components[0]):
                raise NameNotFoundError(components[0])

            next_context = self._get_next_context(components[0])
            obj = next_context.lookup("/".join(components[1:]))

        return obj

    # fixme: Non-JNDI
    def lookup_binding(self, name):
        """ Looks up the binding for a name relative to this context. """

        if len(name) == 0:
            raise InvalidNameError("empty name")

        # Parse the name.
        components = self._parse_name(name)

        # If there is exactly one component in the name then the operation
        # takes place in this context.
        if len(components) == 1:
            atom = components[0]

            if not self._is_bound(atom):
                raise NameNotFoundError(name)

            # Do the actual lookup.
            binding = self._lookup_binding(atom)

        # Otherwise, attempt to continue resolution into the next context.
        else:
            if not self._is_bound(components[0]):
                raise NameNotFoundError(components[0])

            next_context = self._get_next_context(components[0])
            binding = next_context.lookup_binding("/".join(components[1:]))

        return binding

    # fixme: Non-JNDI
    def lookup_context(self, name):
        """Resolves a name relative to this context.

        The name MUST resolve to a context.

        """

        # If the name is empty we return the context itself.
        if len(name) == 0:
            # fixme: The JNDI spec. says that this should return a COPY of
            # the context.
            return self

        # Parse the name.
        components = self._parse_name(name)

        # If there is exactly one component in the name then the operation
        # takes place in this context.
        if len(components) == 1:
            atom = components[0]

            if not self._is_bound(atom):
                raise NameNotFoundError(name)

            # Do the actual lookup.
            obj = self._get_next_context(atom)

        # Otherwise, attempt to continue resolution into the next context.
        else:
            if not self._is_bound(components[0]):
                raise NameNotFoundError(components[0])

            next_context = self._get_next_context(components[0])
            obj = next_context.lookup("/".join(components[1:]))

        return obj

    def create_subcontext(self, name):
        """ Creates a sub-context. """

        if len(name) == 0:
            raise InvalidNameError("empty name")

        # Parse the name.
        components = self._parse_name(name)

        # If there is exactly one component in the name then the operation
        # takes place in this context.
        if len(components) == 1:
            atom = components[0]

            # Is the name already bound?
            if self._is_bound(atom):
                raise NameAlreadyBoundError(name)

            # Do the actual creation of the sub-context.
            sub = self._create_subcontext(atom)

            # Trait event notification.
            self.object_added = NamingEvent(
                new_binding=Binding(name=name, obj=sub, context=self)
            )

        # Otherwise, attempt to continue resolution into the next context.
        else:
            if not self._is_bound(components[0]):
                raise NameNotFoundError(components[0])

            next_context = self._get_next_context(components[0])
            sub = next_context.create_subcontext("/".join(components[1:]))

        return sub

    def destroy_subcontext(self, name):
        """ Destroys a sub-context. """

        if len(name) == 0:
            raise InvalidNameError("empty name")

        # Parse the name.
        components = self._parse_name(name)

        # If there is exactly one component in the name then the operation
        # takes place in this context.
        if len(components) == 1:
            atom = components[0]

            if not self._is_bound(atom):
                raise NameNotFoundError(name)

            obj = self._lookup(atom)
            if not self._is_context(atom):
                raise NotContextError(name)

            # Do the actual destruction of the sub-context.
            self._destroy_subcontext(atom)

            # Trait event notification.
            self.object_removed = NamingEvent(
                old_binding=Binding(name=name, obj=obj, context=self)
            )

        # Otherwise, attempt to continue resolution into the next context.
        else:
            if not self._is_bound(components[0]):
                raise NameNotFoundError(components[0])

            next_context = self._get_next_context(components[0])
            next_context.destroy_subcontext("/".join(components[1:]))

    # fixme: Non-JNDI
    def get_unique_name(self, prefix):
        """Returns a name that is unique within the context.

        The name returned will start with the specified prefix.

        """

        return make_unique_name(
            prefix, existing=self.list_names(""), format="%s (%d)"
        )

    def list_names(self, name=""):
        """ Lists the names bound in a context. """

        # If the name is empty then the operation takes place in this context.
        if len(name) == 0:
            names = self._list_names()

        # Otherwise, attempt to continue resolution into the next context.
        else:
            # Parse the name.
            components = self._parse_name(name)

            if not self._is_bound(components[0]):
                raise NameNotFoundError(components[0])

            next_context = self._get_next_context(components[0])
            names = next_context.list_names("/".join(components[1:]))

        return names

    def list_bindings(self, name=""):
        """ Lists the bindings in a context. """

        # If the name is empty then the operation takes place in this context.
        if len(name) == 0:
            bindings = self._list_bindings()

        # Otherwise, attempt to continue resolution into the next context.
        else:
            # Parse the name.
            components = self._parse_name(name)

            if not self._is_bound(components[0]):
                raise NameNotFoundError(components[0])

            next_context = self._get_next_context(components[0])
            bindings = next_context.list_bindings("/".join(components[1:]))

        return bindings

    # fixme: Non-JNDI
    def is_context(self, name):
        """ Returns True if the name is bound to a context. """

        # If the name is empty then it refers to this context.
        if len(name) == 0:
            is_context = True

        else:
            # Parse the name.
            components = self._parse_name(name)

            # If there is exactly one component in the name then the operation
            # takes place in this context.
            if len(components) == 1:
                atom = components[0]

                if not self._is_bound(atom):
                    raise NameNotFoundError(name)

                # Do the actual check.
                is_context = self._is_context(atom)

            # Otherwise, attempt to continue resolution into the next context.
            else:
                if not self._is_bound(components[0]):
                    raise NameNotFoundError(components[0])

                next_context = self._get_next_context(components[0])
                is_context = next_context.is_context("/".join(components[1:]))

        return is_context

    # fixme: Non-JNDI
    def search(self, obj):
        """ Returns a list of namespace names that are bound to obj. """

        # don't look for None
        if obj is None:
            return []

        # Obj is bound to these names relative to this context
        names = []

        # path contain the name components down to the current context
        path = []

        self._search(obj, names, path, {})

        return names

    ###########################################################################
    # Protected 'Context' interface.
    ###########################################################################

    def _parse_name(self, name):
        """Parse a name into a list of components.

        e.g. 'foo/bar/baz' -> ['foo', 'bar', 'baz']

        """

        return name.split("/")

    def _is_bound(self, name):
        """ Is a name bound in this context? """

        return name in self._bindings

    def _lookup(self, name):
        """ Looks up a name in this context. """

        obj = self._bindings[name]

        return naming_manager.get_object_instance(obj, name, self)

    def _lookup_binding(self, name):
        """ Looks up the binding for a name in this context. """

        return Binding(name=name, obj=self._lookup(name), context=self)

    def _bind(self, name, obj):
        """ Binds a name to an object in this context. """

        state = naming_manager.get_state_to_bind(obj, name, self)
        self._bindings[name] = state

    def _rebind(self, name, obj):
        """ Rebinds a name to an object in this context. """

        self._bind(name, obj)

    def _unbind(self, name):
        """ Unbinds a name from this context. """

        del self._bindings[name]

    def _rename(self, old_name, new_name):
        """ Renames an object in this context. """

        # Bind the new name.
        self._bindings[new_name] = self._bindings[old_name]

        # Unbind the old one.
        del self._bindings[old_name]

    def _create_subcontext(self, name):
        """ Creates a sub-context of this context. """

        sub = self.__class__(environment=self.environment)
        self._bindings[name] = sub

        return sub

    def _destroy_subcontext(self, name):
        """ Destroys a sub-context of this context. """

        del self._bindings[name]

    def _list_bindings(self):
        """ Lists the bindings in this context. """

        bindings = []
        for name in self._list_names():
            bindings.append(
                Binding(name=name, obj=self._lookup(name), context=self)
            )

        return bindings

    def _list_names(self):
        """ Lists the names bound in this context. """

        return list(self._bindings.keys())

    def _is_context(self, name):
        """ Returns True if a name is bound to a context. """

        return self._get_next_context(name) is not None

    def _get_next_context(self, name):
        """ Returns the next context. """

        obj = self._lookup(name)

        # If the object is a context then everything is just dandy.
        if isinstance(obj, Context):
            next_context = obj
        else:
            raise NotContextError(name)

        return next_context

    def _search(self, obj, names, path, searched):
        """Append to names any name bound to obj.
        Join path and name with '/' to for a complete name from the
        top context.
        """

        # Check the bindings recursively.
        for binding in self.list_bindings():
            if binding.obj is obj:
                path.append(binding.name)
                names.append("/".join(path))
                path.pop()

            if (
                isinstance(binding.obj, Context)
                and binding.obj not in searched
            ):
                path.append(binding.name)
                searched[binding.obj] = True
                binding.obj._search(obj, names, path, searched)
                path.pop()
