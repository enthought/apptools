""" Context adapter for Python dictionaries. """


# Enthought library imports.
from apptools.naming.api import Binding, ContextAdapter, naming_manager


class DictContextAdapter(ContextAdapter):
    """ Context adapter for Python dictionaries. """

    #### 'ContextAdapter' interface ###########################################

    # The object that we are adapting.
    #
    #
    # fixme: We would like to specialize the 'adaptee' trait here, but if we
    # make it of type 'Dict' then, on assignment, traits will create a *copy*
    # of the actual dict which I think you'll agree is not very adapter-like!
##     adaptee = Dict

    ###########################################################################
    # Protected 'Context' interface.
    ###########################################################################

    def _is_bound(self, name):
        """ Is a name bound in this context? """

        return name in self.adaptee

    def _lookup(self, name):
        """ Looks up a name in this context. """

        obj = self.adaptee[name]

        return naming_manager.get_object_instance(obj, name, self)

    def _lookup_binding(self, name):
        """ Looks up the binding for a name in this context. """

        return Binding(name=name, obj=self._lookup(name), context=self)

    def _bind(self, name, obj):
        """ Binds a name to an object in this context. """

        state = naming_manager.get_state_to_bind(obj, name, self)
        self.adaptee[name] = state

        return

    def _rebind(self, name, obj):
        """ Rebinds a name to an object in this context. """

        self._bind(name, obj)

        return

    def _unbind(self, name):
        """ Unbinds a name from this context. """

        del self.adaptee[name]

        return

    def _rename(self, old_name, new_name):
        """ Renames an object in this context. """

        # Bind the new name.
        self._bind(new_name, self._lookup(old_name))

        # Unbind the old one.
        self._unbind(old_name)

        return

    def _create_subcontext(self, name):
        """ Creates a sub-context of this context. """

        # Create a dictionary of the same type as the one we are adapting.
        sub = type(self.adaptee)()

        self.adaptee[name] = sub

        return DictContextAdapter(adaptee=sub)

    def _destroy_subcontext(self, name):
        """ Destroys a sub-context of this context. """

        del self.adaptee[name]

        return

    def _list_bindings(self):
        """ Lists the bindings in this context. """

        bindings = []
        for key in self.adaptee:
            bindings.append(
                Binding(name=str(key), obj=self._lookup(key), context=self)
            )

        return bindings

    def _list_names(self):
        """ Lists the names bound in this context. """

        return [str(key) for key in self.adaptee]

#### EOF ######################################################################
