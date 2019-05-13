""" Context adapter for Python lists. """


# Enthought library imports.
from apptools.naming.api import Binding, ContextAdapter, naming_manager
from traits.api import List, Property


class ListContextAdapter(ContextAdapter):
    """ Context adapter for Python lists. """

    #### 'ContextAdapter' interface ###########################################

    # The object that we are adapting.
    #
    # fixme: We would like to specialize the 'adaptee' trait here, but if we
    # make it of type 'List' then, on assignment, traits will create a *copy*
    # of the actual list which I think you'll agree is not very adapter-like!
##     adaptee = List

    #### 'ListContextAdapter' interface #######################################

    # The list that we are adapting.
    collection = Property(List)

    ###########################################################################
    # Protected 'Context' interface.
    ###########################################################################

    def _is_bound(self, name):
        """ Is a name bound in this context? """

        return name in self._list_names()

    def _lookup(self, name):
        """ Looks up a name in this context. """

        binding = self._get_binding_with_name(name)

        return naming_manager.get_object_instance(binding.obj, name, self)

    def _bind(self, name, obj):
        """ Binds a name to an object in this context. """

        state = naming_manager.get_state_to_bind(obj, name, self)
        self.collection.append(state)

        return

    def _rebind(self, name, obj):
        """ Rebinds a name to an object in this context. """

        index = 0
        for binding in self.list_bindings(''):
            if binding.name == name:
                self.collection[index] = obj
                break

            index = index + 1

        # The name is not already bound.
        else:
            self._bind(name, obj)

        return

    def _unbind(self, name):
        """ Unbinds a name from this context. """

        index = 0
        for binding in self.list_bindings(''):
            if binding.name == name:
                del self.collection[index]
                break

            index = index + 1

        else:
            raise SystemError('no binding with name %s' % name)

        return

    def _rename(self, old_name, new_name):
        """ Renames an object in this context. """

        binding = self._get_binding_with_name(old_name)

        self._set_name(binding.obj, new_name)

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

        for obj in self.collection:
            # Bindings have to have a string name.
            name = self._get_name(obj)

            # Create the binding.
            bindings.append(Binding(name=name, obj=obj, context=self))

        return bindings

    def _list_names(self):
        """ Lists the names bound in this context. """

        return [self._get_name(obj) for obj in self.collection]

    ###########################################################################
    # Protected 'ListContext' interface.
    ###########################################################################

    def _get_collection(self):
        """ Returns the collection that we are adapting. """

        return self.adaptee

    ###########################################################################
    # Private interface.
    ###########################################################################

    # fixme: Allow an item name trait to be specified instead of guessing at
    # 'name' or 'id'!
    def _get_name(self, obj):
        """ Returns the name of an object. """

        if hasattr(obj, 'name'):
            name = str(obj.name)

        elif hasattr(obj, 'id'):
            name = str(obj.id)

        else:
            name = str(obj)

        return name

    def _set_name(self, obj, name):
        """ Sets the name of an object. """

        if hasattr(obj, 'name'):
            obj.name = name

        elif hasattr(obj, 'id'):
            obj.id = name

        return

    def _get_binding_with_name(self, name):
        """ Returns the binding with the specified name. """

        for binding in self.list_bindings(''):
            if binding.name == name:
                break

        # The reason that this is a system error and not just a naming error
        # is that this method is only called from inside the protected
        # 'Context' interface when we have already determined that the name
        # is bound
        else:
            raise SystemError('no binding with name %s' % name)

        return binding

#### EOF ######################################################################
