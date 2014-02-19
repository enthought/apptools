from traits.api import Dict, HasTraits

from apptools.selection.errors import SelectionProviderNotFoundError


class SelectionService(HasTraits):

    _providers = Dict()

    def add_selection_provider(self, provider):
        """ """
        self._providers[provider.id] = provider

    def has_selection_provider(self, provider):
        return provider.id in self._providers

    def remove_selection_provider(self, provider):
        if not self.has_selection_provider(provider):
            raise SelectionProviderNotFoundError(provider_id=provider.id)
        del self._providers[provider.id]

    def get_selection(self, id):
        provider = self._providers[id]
        return provider.get_selection()
