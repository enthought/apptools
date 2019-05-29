""" A generic object factory. """


# Enthought library imports.
from traits.api import Any

# Local imports.
from .abstract_factory import AbstractFactory


class Factory(AbstractFactory):
    """ A generic object factory.

    This implementation of the abstract factory interface provides for the
    common scenario where the factory produces objects of exactly one type.

    """

    #### 'Factory' interface ##################################################

    # The type of object that we create.
    #
    # fixme: This trait definition should be 'Class' but currently this only
    # allows old-style classes!
    target_class = Any

    ###########################################################################
    # 'AbstractFactory' interface.
    ###########################################################################

    def can_create(self, target_class, *args, **kw):
        """ Returns True if the factory can create objects of a class. """

        return target_class is self.target_class

    def create(self, *args, **kw):
        """ Creates an object! """

        return self.target_class(*args, **kw)

#### EOF ######################################################################
