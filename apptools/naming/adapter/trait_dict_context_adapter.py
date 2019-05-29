""" Context adapter for trait dictionaries. """


# Enthought library imports.
from traits.api import Dict, Property, Str

# Local imports.
from .dict_context_adapter import DictContextAdapter


class TraitDictContextAdapter(DictContextAdapter):
    """ Context adapter for trait dictionaries. """

    #### 'Context' interface ##################################################

    # The name of the context within its own namespace.
    namespace_name = Property(Str)

    #### 'ContextAdapter' interface ###########################################

    # The object that we are adapting.
    adaptee = Dict

    #### 'TraitDictContextAdapter' interface ##################################

    # The name of the object's trait that provides the dictionary.
    trait_name = Str

    ###########################################################################
    # 'Context' interface.
    ###########################################################################

    def _get_namespace_name(self):
        """ Returns the name of the context within its own namespace. """

        return self.context.namespace_name + '/' + self.trait_name

#### EOF ######################################################################
