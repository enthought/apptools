#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Enthought, Inc.
# Description: <Enthought naming package component>
#------------------------------------------------------------------------------
""" A naming context for a Python namespace. """


# Enthought library imports.
from traits.api import Any, Dict, Instance, Property

# Local imports.
from .address import Address
from .binding import Binding
from .context import Context
from .naming_manager import naming_manager
from .py_object_factory import PyObjectFactory
from .reference import Reference
from .referenceable import Referenceable
from .referenceable_state_factory import ReferenceableStateFactory


# The default environment.
ENVIRONMENT = {
    # 'Context' properties.
    Context.OBJECT_FACTORIES : [PyObjectFactory()],
    Context.STATE_FACTORIES  : [ReferenceableStateFactory()],
}


class PyContext(Context, Referenceable):
    """ A naming context for a Python namespace. """

    #### 'Context' interface ##################################################

    # The naming environment in effect for this context.
    environment = Dict(ENVIRONMENT)

    #### 'PyContext' interface ################################################

    # The Python namespace that we represent.
    namespace = Any

    # If the namespace is actual a Python object that has a '__dict__'
    # attribute, then this will be that object (the namespace will be the
    # object's '__dict__'.
    obj = Any

    #### 'Referenceable' interface ############################################

    # The object's reference suitable for binding in a naming context.
    reference = Property(Instance(Reference))

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **traits):
        """ Creates a new context. """

        # Base class constructor.
        super(PyContext, self).__init__(**traits)

        if type(self.namespace) is not dict:
            if hasattr(self.namespace, '__dict__'):
                self.obj = self.namespace
                self.namespace = self.namespace.__dict__

            else:
                raise ValueError('Need a dictionary or a __dict__ attribute')

        return

    ###########################################################################
    # 'Referenceable' interface.
    ###########################################################################

    #### Properties ###########################################################

    def _get_reference(self):
        """ Returns a reference to this object suitable for binding. """

        reference = Reference(
            class_name = self.__class__.__name__,
            addresses  = [Address(type='py_context', content=self.namespace)]
        )

        return reference

    ###########################################################################
    # Protected 'Context' interface.
    ###########################################################################

    def _is_bound(self, name):
        """ Is a name bound in this context? """

        return name in self.namespace

    def _lookup(self, name):
        """ Looks up a name in this context. """

        obj = self.namespace[name]

        return naming_manager.get_object_instance(obj, name, self)

    def _bind(self, name, obj):
        """ Binds a name to an object in this context. """

        state = naming_manager.get_state_to_bind(obj, name,self)
        self.namespace[name] = state

        # Trait event notification.
        # An "added" event is fired by the bind method of the base calss (which calls
        # this one), so we don't need to do the changed here (which would be the wrong
        # thing anyway) -- LGV
        #
        # self.trait_property_changed('context_changed', None, None)

        return

    def _rebind(self, name, obj):
        """ Rebinds a name to a object in this context. """

        self._bind(name, obj)

        return

    def _unbind(self, name):
        """ Unbinds a name from this context. """

        del self.namespace[name]

        # Trait event notification.
        self.trait_property_changed('context_changed', None, None)

        return

    def _rename(self, old_name, new_name):
        """ Renames an object in this context. """

        state = self.namespace[old_name]

        # Bind the new name.
        self.namespace[new_name] = state

        # Unbind the old one.
        del self.namespace[old_name]

        # Trait event notification.
        self.context_changed = True

        return

    def _create_subcontext(self, name):
        """ Creates a sub-context of this context. """

        sub = self._context_factory(name, {})
        self.namespace[name] = sub

        # Trait event notification.
        self.trait_property_changed('context_changed', None, None)

        return sub

    def _destroy_subcontext(self, name):
        """ Destroys a sub-context of this context. """

        del self.namespace[name]

        # Trait event notification.
        self.trait_property_changed('context_changed', None, None)

        return

    def _list_bindings(self):
        """ Lists the bindings in this context. """

        bindings = []
        for name, value in self.namespace.items():
            bindings.append(Binding(name=name, obj=self._lookup(name),
                                    context=self))
        return bindings

    def _list_names(self):
        """ Lists the names bound in this context. """

        return list(self.namespace.keys())

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _context_factory(self, name, namespace):
        """ Create a sub-context. """

        return self.__class__(namespace=namespace)

#### EOF ######################################################################
