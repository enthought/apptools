""" Context adapter for Python tuples. """


# Enthought library imports.
from traits.api import Tuple

# Local imports.
from .list_context_adapter import ListContextAdapter


class TupleContextAdapter(ListContextAdapter):
    """ Context adapter for Python tuples. """

    #### 'ContextAdapter' interface ###########################################

    # The object that we are adapting.
    adaptee = Tuple

#### EOF ######################################################################
