""" Context adapter factory for Python tuple. """


# Enthought library imports.
from apptools.naming.api import ContextAdapterFactory

# Local imports.
from .tuple_context_adapter import TupleContextAdapter


class TupleContextAdapterFactory(ContextAdapterFactory):
    """ Context adapter factoryfor Python tuples. """

    #### 'ContextAdapterFactory' interface ####################################

    # The type of object that we adapt.
    adaptee_class = tuple

    ###########################################################################
    # Protected 'AbstractAdapterFactory' interface.
    ###########################################################################

    def _adapt(self, adaptee, target_class, environment, context):
        """ Returns an adapter that adapts an object to the target class. """

        adapter = TupleContextAdapter(
            adaptee     = adaptee,
            environment = environment,
            context     = context
        )

        return adapter

#### EOF ######################################################################
