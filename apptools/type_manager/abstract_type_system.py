""" The abstract base class for type systems. """


# Enthought library imports.
from traits.api import HasTraits


class AbstractTypeSystem(HasTraits):
    """ The abstract base class for type systems.

    A type system is responsible for:-

    1) Determining whether an object is of a particular type.
    2) Determining the MRO of a type.

    See 'PythonTypeSystem' for an implementation with standard Python
    semantics.

    """

    ###########################################################################
    # 'AbstractTypeSystem' interface.
    ###########################################################################

    def is_a(self, obj, type):
        """ Is an object an instance of the specified type? """

        raise NotImplementedError

    def get_mro(self, type):
        """ Returns the MRO of a type. """

        raise NotImplementedError

#### EOF ######################################################################
