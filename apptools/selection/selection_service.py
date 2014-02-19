from traits.api import Dict, HasTraits

from apptools.selection.errors import (SelectionProviderNotFoundError,
                                       IDConflictError)


class SelectionService(HasTraits):

    #### 'SelectionService' protocol ##########################################

    def add_selection_provider(self, provider):
        """ """
        if self.has_selection_provider(provider.id):
            raise IDConflictError(provider_id=provider.id)
        self._providers[provider.id] = provider

    def has_selection_provider(self, id):
        return id in self._providers

    def remove_selection_provider(self, provider):
        self._raise_if_not_registered(provider.id)
        del self._providers[provider.id]

    def get_selection(self, id):
        self._raise_if_not_registered(id)
        provider = self._providers[id]
        return provider.get_selection()

    #### Private protocol #####################################################

    _providers = Dict()

    def _raise_if_not_registered(self, id):
        if not self.has_selection_provider(id):
            raise SelectionProviderNotFoundError(provider_id=id)
