""" A default adapter class. """


# Enthought library imports.
from traits.api import Any, HasTraits


class Adapter(HasTraits):
    """ A default adapter class.

    This comes in handy when using the default 'AdapterFactory' as it expects
    the adpter class to have an 'adaptee' trait.

    """

    #### 'Adapter' interface ##################################################

    # The object that we are adapting.
    adaptee = Any

#### EOF ######################################################################
