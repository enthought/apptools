""" Context adapter factory for Python lists. """


# Enthought library imports.
from apptools.naming.api import ContextAdapterFactory

# Local imports.
from .list_context_adapter import ListContextAdapter


class ListContextAdapterFactory(ContextAdapterFactory):
    """ Context adapter factory for Python lists. """

    #### 'ContextAdapterFactory' interface ####################################

    # The type of object that we adapt.
    adaptee_class = list

    ###########################################################################
    # Protected 'AbstractAdapterFactory' interface.
    ###########################################################################

    def _adapt(self, adaptee, target_class, environment, context):
        """ Returns an adapter that adapts an object to the target class. """

        adapter = ListContextAdapter(
            adaptee     = adaptee,
            environment = environment,
            context     = context
        )

        return adapter

#### EOF ######################################################################
