""" A manager for adapter factories. """

# Standard library imports
import warnings

# Third-party imports
import six

# Enthought library imports.
from traits.api import Dict, HasTraits, Instance, Property

# Local imports.
from .abstract_type_system import AbstractTypeSystem
from .python_type_system import PythonTypeSystem


class AdapterManager(HasTraits):
    """ A manager for adapter factories. """

    #### 'AdapterManager' interface ###########################################

    # All registered type-scope factories by the type of object that they
    # adapt.
    #
    # The dictionary is keyed by the *name* of the class rather than the class
    # itself to allow for adapter factory proxies to register themselves
    # without having to load and create the factories themselves (i.e., to
    # allow us to lazily load adapter factories contributed by plugins). This
    # is a slight compromise as it is obviously geared towards use in Envisage,
    # but it doesn't affect the API other than allowing a class OR a string to
    # be passed to 'register_adapters'.
    #
    # { String adaptee_class_name : List(AdapterFactory) factories }
    type_factories = Property(Dict)

    # All registered instance-scope factories by the object that they adapt.
    #
    # { id(obj) : List(AdapterFactory) factories }
    instance_factories = Property(Dict)

    # The type system used by the manager (it determines 'is_a' relationships
    # and type MROs etc). By default we use standard Python semantics.
    type_system = Instance(AbstractTypeSystem, PythonTypeSystem())

    #### Private interface ####################################################

    # All registered type-scope factories by the type of object that they
    # adapt.
    _type_factories = Dict

    # All registered instance-scope factories by the object that they adapt.
    _instance_factories = Dict

    ###########################################################################
    # 'AdapterManager' interface.
    ###########################################################################

    #### Properties ###########################################################

    def _get_type_factories(self):
        """ Returns all registered type-scope factories. """

        return self._type_factories.copy()

    def _get_instance_factories(self):
        """ Returns all registered instance-scope factories. """

        return self._instance_factories.copy()

    #### Methods ##############################################################

    def adapt(self, adaptee, target_class, *args, **kw):
        """ Returns an adapter that adapts an object to the target class.

        'adaptee' is the object that we want to adapt.
        'target_class' is the class that the adaptee should be adapted to.

        Returns None if no such adapter exists.

        """

        # If the object is already an instance of the target class then we
        # simply return it.
        if self.type_system.is_a(adaptee, target_class):
            adapter = adaptee

        # Otherwise, look at each class in the adaptee's MRO to see if there
        # is an adapter factory registered that can adapt the object to the
        # target class.
        else:
            # Look for instance-scope adapters first.
            adapter = self._adapt_instance(adaptee, target_class, *args, **kw)

            # If no instance-scope adapter was found then try type-scope
            # adapters.
            if adapter is None:
                for adaptee_class in self.type_system.get_mro(type(adaptee)):
                    adapter = self._adapt_type(
                        adaptee, adaptee_class, target_class, *args, **kw
                    )
                    if adapter is not None:
                        break

        return adapter

    def register_instance_adapters(self, factory, obj):
        """ Registers an instance-scope adapter factory.

        A factory can be in exactly one manager (as it uses the manager's type
        system).

        """

        factories = self._instance_factories.setdefault(id(obj), [])
        factories.append(factory)

        # A factory can be in exactly one manager.
        factory.adapter_manager = self

        return

    def unregister_instance_adapters(self, factory, obj):
        """ Unregisters an instance scope adapter factory.

        A factory can be in exactly one manager (as it uses the manager's type
        system).

        """

        factories = self._instance_factories.setdefault(id(obj), [])
        if factory in factories:
            factories.remove(factory)

        # A factory can be in exactly one manager.
        factory.adapter_manager = None

        return

    def register_type_adapters(self, factory, adaptee_class):
        """ Registers a type-scope adapter factory.

        'adaptee_class' can be either a class object or the name of a class.

        A factory can be in exactly one manager (as it uses the manager's type
        system).

        """

        if isinstance(adaptee_class, six.string_types):
            adaptee_class_name = adaptee_class

        else:
            adaptee_class_name = self._get_class_name(adaptee_class)

        factories = self._type_factories.setdefault(adaptee_class_name, [])
        factories.append(factory)

        # A factory can be in exactly one manager.
        factory.adapter_manager = self

        return

    def unregister_type_adapters(self, factory):
        """ Unregisters a type-scope adapter factory. """

        for adaptee_class_name, factories in self._type_factories.items():
            if factory in factories:
                factories.remove(factory)

        # The factory is no longer deemed to be part of this manager.
        factory.adapter_manager = None

        return

    #### DEPRECATED ###########################################################

    def register_adapters(self, factory, adaptee_class):
        """ Registers an adapter factory.

        'adaptee_class' can be either a class object or the name of a class.

        A factory can be in exactly one manager (as it uses the manager's type
        system).

        """

        warnings.warn(
            'Use "register_type_adapters" instead.',
            DeprecationWarning
        )

        self.register_type_adapters(factory, adaptee_class)

        return

    def unregister_adapters(self, factory):
        """ Unregisters an adapter factory. """

        warnings.warn(
            'use "unregister_type_adapters" instead.',
            DeprecationWarning
        )

        self.unregister_type_adapters(factory)

        return

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _adapt_instance(self, adaptee, target_class, *args, **kw):
        """ Returns an adapter that adaptes an object to the target class.

        Returns None if no such adapter exists.

        """

        for factory in self._instance_factories.get(id(adaptee), []):
            adapter = factory.adapt(adaptee, target_class, *args, **kw)
            if adapter is not None:
                break

        else:
            adapter = None

        return adapter

    def _adapt_type(self, adaptee, adaptee_class, target_class, *args, **kw):
        """ Returns an adapter that adapts an object to the target class.

        Returns None if no such adapter exists.

        """

        adaptee_class_name = self._get_class_name(adaptee_class)

        for factory in self._type_factories.get(adaptee_class_name, []):
            adapter = factory.adapt(adaptee, target_class, *args, **kw)
            if adapter is not None:
                break

        else:
            adapter = None

        return adapter

    def _get_class_name(self, klass):
        """ Returns the full class name for a class. """

        return "%s.%s" % (klass.__module__, klass.__name__)

#### EOF ######################################################################
