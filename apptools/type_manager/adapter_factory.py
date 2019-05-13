""" An adapter factory. """


# Enthought library imports.
from traits.api import Any

# Local imports.
from .abstract_adapter_factory import AbstractAdapterFactory


class AdapterFactory(AbstractAdapterFactory):
    """ An adapter factory.

    This implementation provides the common case where the factory adapts
    exactly one type of object to exactly one target type using exactly one
    adapter.

    This class requires the adapter class to have an 'adaptee' trait. The
    default 'Adapter' class provides exactly that.

    """

    #### 'AdapterFactory' interface ###########################################

    # fixme: These trait definitions should be 'Class' but currently this only
    # allows old-style classes!
    #
    # The type of object that the factory can adapt.
    adaptee_class = Any

    # The adapter class (the class that adapts the adaptee to the target
    # class).
    adapter_class = Any

    # The target class (the class that the factory can adapt objects to).
    target_class = Any

    ###########################################################################
    # Protected 'AbstractAdapterFactory' interface.
    ###########################################################################

    def _can_adapt(self, adaptee, target_class, *args, **kw):
        """ Returns True if the factory can produce an appropriate adapter. """

        can_adapt = target_class is self.target_class \
                    and self.type_system.is_a(adaptee, self.adaptee_class)

        return can_adapt

    def _adapt(self, adaptee, target_class, *args, **kw):
        """ Returns an adapter that adapts an object to the target class.

        This requires the adapter class to have an 'adaptee' trait. The default
        'Adapter' class provides exactly that.

        """

        return self.adapter_class(adaptee=adaptee, *args, **kw)

#### EOF ######################################################################
