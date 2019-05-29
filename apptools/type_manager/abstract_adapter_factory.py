""" Abstract base class for all adapter factories. """

# Standard library imports.
import logging

# Enthought library imports.
from traits.api import Delegate, HasTraits, Instance

# Local imports.
from .adapter_manager import AdapterManager


logger = logging.getLogger(__name__)


class AbstractAdapterFactory(HasTraits):
    """ Abstract base class for all adapter factories.

    Adapter factories define behavioural extensions for classes.

    """

    #### 'AbstractAdapterFactory' interface ###################################

    # The adapter manager that the factory is registered with (this will be
    # None iff the factory is not registered with a manager).
    adapter_manager = Instance(AdapterManager)

    # The type system used by the factory (it determines 'is_a' relationships
    # and type MROs etc). By default we use standard Python semantics.
    type_system = Delegate('adapter_manager')

    ###########################################################################
    # 'AbstractAdapterFactory' interface.
    ###########################################################################

    def adapt(self, adaptee, target_class, *args, **kw):
        """ Returns an adapter that adapts an object to the target class.

        Returns None if the factory cannot produce such an adapter.

        """

        if self._can_adapt(adaptee, target_class, *args, **kw):
            adapter = self._adapt(adaptee, target_class, *args, **kw)
            if adapter is None:
                logger.warn(self._get_warning_message(adaptee, target_class))

        else:
            adapter = None

        return adapter

    ###########################################################################
    # Protected 'AbstractAdapterFactory' interface.
    ###########################################################################

    def _can_adapt(self, adaptee, target_class, *args, **kw):
        """ Returns True if the factory can produce an appropriate adapter. """

        raise NotImplementedError

    def _adapt(self, adaptee, target_class, *args, **kw):
        """ Returns an adapter that adapts an object to the target class. """

        raise NotImplementedError

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _get_warning_message(self, adaptee, target_class):
        """ Returns a warning message.

        The warning message is used when a factory fails to adapt something
        that it said it could!

        """

        message = '%s failed to adapt %s to %s' % (
            self.__class__.__name__,
            str(adaptee),
            target_class.__name__
        )

        return message

#### EOF ######################################################################
