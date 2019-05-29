""" Context adapter for trait lists. """


# Enthought library imports.
from traits.api import Any, List, Property, Str

# Local imports.
from .list_context_adapter import ListContextAdapter


class TraitListContextAdapter(ListContextAdapter):
    """ Context adapter for trait lists. """

    #### 'Context' interface ##################################################

    # The name of the context within its own namespace.
    namespace_name = Property(Str)

    #### 'ContextAdapter' interface ###########################################

    # The object that we are adapting.
    adaptee = Any

    #### 'ListContextAdapter' interface #######################################

    # The list that we are adapting.
    collection = Property(List)

    #### 'TraitListContextAdapter' interface ##################################

    # The name of the object's trait that provides the list.
    trait_name = Str

    ###########################################################################
    # 'Context' interface.
    ###########################################################################

    def _get_namespace_name(self):
        """ Returns the name of the context within its own namespace. """

        return self.context.namespace_name + '/' + self.trait_name

    ###########################################################################
    # Protected 'ListContext' interface.
    ###########################################################################

    #### 'Properties' #########################################################

    def _get_collection(self):
        """ Returns the collection that we are adapting. """

        components = self.trait_name.split('.')
        if len(components) == 1:
            collection = getattr(self.adaptee, self.trait_name)

        else:
            # Find the object that contains the trait.
            obj = self.adaptee
            for component in components[:-1]:
                obj = getattr(obj, component)

            collection = getattr(obj, components[-1])

        return collection

#### EOF ######################################################################
