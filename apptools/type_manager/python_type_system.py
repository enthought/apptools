""" A type system with standard(ish) Python semantics. """


# Standard library imports.
import inspect

# Local imports.
from .abstract_type_system import AbstractTypeSystem


class PythonObject:
    """ The root type in the type system.

    fixme: Python is currently a bit broken as it has dual type hierarchies,
    one for old-style and one for new-style classes. This class is used to
    create a fake root to unify them.

    """

    __class__ = type


class PythonTypeSystem(AbstractTypeSystem):
    """ A type system with standard(ish) Python semantics. """

    ###########################################################################
    # 'AbstractTypeSystem' interface.
    ###########################################################################

    def is_a(self, obj, type):
        """ Is an object and instance of the specified type? """

        return isinstance(obj, type) or type is PythonObject

    def get_mro(self, type):
        """ Returns the MRO of a type. """

        return list(inspect.getmro(type)) + [PythonObject]

#### EOF ######################################################################
