""" A type manager. """


# Enthought library imports.
from traits.api import HasTraits, Instance, Property, Str

# Local imports.
from .abstract_type_system import AbstractTypeSystem
from .adapter_manager import AdapterManager
from .factory import Factory
from .hook import add_pre, add_post, remove_pre, remove_post
from .python_type_system import PythonTypeSystem


class TypeManager(HasTraits):
    """ A type manager.

    The type manager allows for objects to be created/adapted to a particular
    type.

    """

    #### 'TypeManager' interface ##############################################

    # The adapter manager looks after errr, all adapters.
    adapter_manager = Property(Instance(AdapterManager))

    # The type manager's globally unique identifier (only required if you have
    # more than one type manager of course!).
    id = Str

    # The parent type manager.
    #
    # By default this is None, but you can use it to set up a hierarchy of
    # type managers. If a type manager fails to adapt or create an object of
    # some target class then it will give its parent a chance to do so.
    parent = Instance('TypeManager')

    # The type system used by the manager (it determines 'is_a' relationships
    # and type MROs etc).
    #
    # By default we use standard Python semantics.
    type_system = Instance(AbstractTypeSystem, PythonTypeSystem())

    #### Private interface ####################################################

    # The adapter manager looks after errr, all adapters.
    _adapter_manager = Instance(AdapterManager)

    ###########################################################################
    # 'TypeManager' interface.
    ###########################################################################

    #### Properties ###########################################################

    def _get_adapter_manager(self):
        """ Returns the adapter manager. """

        return self._adapter_manager

    #### Methods ##############################################################

    def object_as(self, obj, target_class, *args, **kw):
        """ Adapts or creates an object of the target class.

        Returns None if no appropriate adapter or factory is available.

        """

        # If the object is already an instance of the target class then we
        # simply return it.
        if self.type_system.is_a(obj, target_class):
            result = obj

        # If the object is a factory that creates instances of the target class
        # then ask it to produce one.
        elif self._is_factory_for(obj, target_class, *args, **kw):
            result = obj.create(target_class, *args, **kw)

        # Otherwise, see if the object can be adapted to the target class.
        else:
            result = self._adapter_manager.adapt(obj, target_class, *args,**kw)

        # If this type manager couldn't do the job, then give its parent a go!
        if result is None and self.parent is not None:
            result = self.parent.object_as(obj, target_class, *args, **kw)

        return result

    # Adapters.
    def register_adapters(self, factory, adaptee_class):
        """ Registers an adapter factory.

        'adaptee_class' can be either a class or the name of a class.

        """

        self._adapter_manager.register_adapters(factory, adaptee_class)

        return

    def unregister_adapters(self, factory):
        """ Unregisters an adapter factory. """

        self._adapter_manager.unregister_adapters(factory)

        return

    def register_instance_adapters(self, factory, obj):
        """ Registers an adapter factory for an individual instance.

        A factory can be in exactly one manager (as it uses the manager's type
        system).

        """

        self._adapter_manager.register_instance_adapters(factory, obj)

        return

    def unregister_instance_adapters(self, factory, obj):
        """ Unregisters an adapter factory for an individual instance.

        A factory can be in exactly one manager (as it uses the manager's type
        system).

        """

        self._adapter_manager.unregister_instance_adapters(factory, obj)

        return

    def register_type_adapters(self, factory, adaptee_class):
        """ Registers an adapter factory.

        'adaptee_class' can be either a class or the name of a class.

        """

        self._adapter_manager.register_type_adapters(factory, adaptee_class)

        return

    def unregister_type_adapters(self, factory):
        """ Unregisters an adapter factory. """

        self._adapter_manager.unregister_type_adapters(factory)

        return

    # Categories.
    #
    # Currently, there is no technical reason why we have this convenience
    # method to add categories. However, it may well turn out to be useful to
    # track all categories added via the type manager.
    def add_category(self, klass, category_class):
        """ Adds a category to a class. """

        klass.add_trait_category(category_class)

        return

    # Hooks.
    #
    # Currently, there is no technical reason why we have these convenience
    # methods to add and remove hooks. However, it may well turn out to be
    # useful to track all hooks added via the type manager.
    def add_pre(self, klass, method_name, callable):
        """ Adds a pre-hook to method 'method_name' on class 'klass. """

        add_pre(klass, method_name, callable)

        return

    def add_post(self, klass, method_name, callable):
        """ Adds a post-hook to method 'method_name' on class 'klass. """

        add_post(klass, method_name, callable)

        return

    def remove_pre(self, klass, method_name, callable):
        """ Removes a pre-hook to method 'method_name' on class 'klass. """

        remove_pre(klass, method_name, callable)

        return

    def remove_post(self, klass, method_name, callable):
        """ Removes a post-hook to method 'method_name' on class 'klass. """

        remove_post(klass, method_name, callable)

        return

    ###########################################################################
    # Private interface.
    ###########################################################################

    #### Initializers #########################################################

    def __adapter_manager_default(self):
        """ Initializes the '_adapter_manager' trait. """

        return AdapterManager(type_system=self.type_system)

    #### Methods ##############################################################

    def _is_factory_for(self, obj, target_class, *args, **kw):
        """ Returns True iff the object is a factory for the target class. """

        is_factory_for = self.type_system.is_a(obj, Factory) \
                         and obj.can_create(target_class, *args, **kw)

        return is_factory_for

#### EOF ######################################################################
