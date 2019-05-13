""" Context adapter factory for trait dicts. """


# Enthought library imports.
from apptools.naming.api import ContextAdapterFactory
from traits.api import Str, TraitDict

# Local imports.
from .trait_dict_context_adapter import TraitDictContextAdapter


class TraitDictContextAdapterFactory(ContextAdapterFactory):
    """ Context adapter factoryfor Python trait dicts. """

    #### 'ContextAdapterFactory' interface ####################################

    # The type of object that we adapt.
    adaptee_class = TraitDict

    #### 'TraitDictContextAdapterFactory' interface ###########################

    # The name of the trait (on the adaptee) that provides the trait dict.
    trait_name = Str

    ###########################################################################
    # Protected 'AbstractAdapterFactory' interface.
    ###########################################################################

    def _adapt(self, adaptee, target_class, environment, context):
        """ Returns an adapter that adapts an object to the target class. """

        adapter = TraitDictContextAdapter(
            adaptee     = adaptee,
            environment = environment,
            context     = context,
            trait_name  = self.trait_name
        )

        return adapter

#### EOF ######################################################################
