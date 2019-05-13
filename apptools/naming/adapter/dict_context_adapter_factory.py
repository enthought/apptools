""" Context adapter factory for Python dictionaries. """


# Enthought library imports.
from apptools.naming.api import ContextAdapterFactory

# Local imports.
from .dict_context_adapter import DictContextAdapter


class DictContextAdapterFactory(ContextAdapterFactory):
    """ Context adapter factory for Python dictionaries. """

    #### 'ContextAdapterFactory' interface ####################################

    # The type of object that we adapt.
    adaptee_class = dict

    ###########################################################################
    # Protected 'AbstractAdapterFactory' interface.
    ###########################################################################

    def _adapt(self, adaptee, target_class, environment, context):
        """ Returns an adapter that adapts an object to the target class. """

        adapter = DictContextAdapter(
            adaptee     = adaptee,
            environment = environment,
            context     = context
        )

        return adapter

#### EOF ######################################################################
