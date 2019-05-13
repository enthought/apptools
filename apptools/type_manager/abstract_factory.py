""" Abstract base class for all object factories. """

# Standard library imports.
import logging

# Enthought library imports.
from traits.api import HasTraits


logger = logging.getLogger(__name__)


class AbstractFactory(HasTraits):
    """ Abstract base class for all object factories. """

    ###########################################################################
    # 'AbstractFactory' interface.
    ###########################################################################

    def create(self, target_class, *args, **kw):
        """ Creates an object of the specified target class.

        Returns None if the factory cannot produce an object of the target
        class.

        """

        if self._can_create(target_class, *args, **kw):
            obj = self._create(target_class, *args, **kw)
            if obj is None:
                logger.warn(self._get_warning_message(target_class))

        else:
            obj = None

        return obj

    ###########################################################################
    # Protected 'AbstractFactory' interface.
    ###########################################################################

    def _can_create(self, target_class, *args, **kw):
        """ Returns True if the factory can create objects of a class. """

        return NotImplementedError

    def _create(self, target_class, *args, **kw):
        """ Creates an object of the specified target class. """

        raise NotImplementedError

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _get_warning_message(self, target_class):
        """ Returns a warning message.

        The warning message is used when a factory fails to create something
        that it said it could!

        """

        message = "%s failed to create a %s" % (
            self.__class__.__name__,
            target_class.__name__
        )

        return message

#### EOF ######################################################################
