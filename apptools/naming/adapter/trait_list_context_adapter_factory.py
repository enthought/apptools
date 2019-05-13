""" Context adapter factory for trait lists. """


# Enthought library imports.
from apptools.naming.api import ContextAdapterFactory
from traits.api import Str, TraitList

# Local imports.
from .trait_list_context_adapter import TraitListContextAdapter


class TraitListContextAdapterFactory(ContextAdapterFactory):
    """ Context adapter factoryfor Python trait lists. """

    #### 'ContextAdapterFactory' interface ####################################

    # The type of object that we adapt.
    adaptee_class = TraitList

    #### 'TraitListContextAdapterFactory' interface ###########################

    # The name of the trait (on the adaptee) that provides the trait list.
    trait_name = Str

    ###########################################################################
    # Protected 'AbstractAdapterFactory' interface.
    ###########################################################################

    def _adapt(self, adaptee, target_class, environment, context):
        """ Returns an adapter that adapts an object to the target class. """

        adapter = TraitListContextAdapter(
            adaptee     = adaptee,
            environment = environment,
            context     = context,
            trait_name  = self.trait_name
        )

        return adapter

#### EOF ######################################################################
