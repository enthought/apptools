""" Context adapter for Python instances. """


# Standard library imports.
import re

# Enthought library imports.
from apptools.naming.api import Binding, ContextAdapter
from apptools.naming.api import OperationNotSupportedError, naming_manager
from traits.api import HasTraits, List, Property, Str


class InstanceContextAdapter(ContextAdapter):
    """ Context adapter for Python instances. """

    #### 'Context' interface ##################################################

    # The name of the context within its own namespace.
    namespace_name = Property(Str)

    #### 'InstanceContextAdapter' interface ###################################

    # By default every public attribute of an instance is exposed. Use the
    # following traits to either include or exclude attributes as appropriate.
    #
    # Regular expressions that describe the names of attributes to include.
    include = List(Str)

    # Regular expressions that describe the names of attributes to exclude.  By
    # default we exclude 'protected' and 'private' attributes and any
    # attributes that are artifacts of the traits mechanism.
    exclude = List(Str, ['_', 'trait_'])

    ###########################################################################
    # 'Context' interface.
    ###########################################################################

    #### Properties ###########################################################

    def _get_namespace_name(self):
        """ Returns the name of the context within its own namespace. """

        base = self.context.namespace_name
        if len(base) > 0:
            base += '/'

        names = self.context.search(self.adaptee)

        return base + names[0]

    ###########################################################################
    # Protected 'Context' interface.
    ###########################################################################

    def _is_bound(self, name):
        """ Is a name bound in this context? """

        return name in self._list_names()

    def _lookup(self, name):
        """ Looks up a name in this context. """

        obj = getattr(self.adaptee, name)

        return naming_manager.get_object_instance(obj, name, self)

    def _lookup_binding(self, name):
        """ Looks up the binding for a name in this context. """

        return Binding(name=name, obj=self._lookup(name), context=self)

    def _bind(self, name, obj):
        """ Binds a name to an object in this context. """

        state = naming_manager.get_state_to_bind(obj, name, self)
        setattr(self.adaptee, name, state)

        return

    def _rebind(self, name, obj):
        """ Rebinds a name to an object in this context. """

        self._bind(name, obj)

        return

    def _unbind(self, name):
        """ Unbinds a name from this context. """

        delattr(self.adaptee, name)

        return

    def _rename(self, old_name, new_name):
        """ Renames an object in this context. """

        # Bind the new name.
        setattr(self.adaptee, new_name, self._lookup(old_name))

        # Unbind the old one.
        delattr(self.adaptee, old_name)

        return

    def _create_subcontext(self, name):
        """ Creates a sub-context of this context. """

        raise OperationNotSupportedError()

    def _destroy_subcontext(self, name):
        """ Destroys a sub-context of this context. """

        raise OperationNotSupportedError()

    def _list_bindings(self):
        """ Lists the bindings in this context. """

        bindings = []
        for name in self._list_names():
            try:
                obj = self._lookup(name)
                bindings.append(Binding(name=name, obj=obj, context=self))

            # We get attribute errors when we try to look up Event traits (they
            # are write-only).
            except AttributeError:
                pass

        return bindings

    def _list_names(self):
        """ Lists the names bound in this context. """

        return self._get_public_attribute_names(self.adaptee)

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _get_public_attribute_names(self, obj):
        """ Returns the names of an object's public attributes. """

        if isinstance(obj, HasTraits):
            names = obj.trait_names()

        elif hasattr(obj, '__dict__'):
            names = list(self.adaptee.__dict__.keys())

        else:
            names = []

        return [name for name in names if self._is_exposed(name)]

    def _is_exposed(self, name):
        """ Returns True iff a name should be exposed. """

        if len(self.include) > 0:
            is_exposed = self._matches(self.include, name)

        elif len(self.exclude) > 0:
            is_exposed = not self._matches(self.exclude, name)

        else:
            is_exposed = True

        return is_exposed

    def _matches(self, expressions, name):
        """ Returns True iff a name matches any of a list of expressions. """

        for expression in expressions:
            if re.match(expression, name) is not None:
                matches = True
                break

        else:
            matches = False

        return matches

#### EOF ######################################################################
