from traits.api import Dict, HasTraits

from apptools.selection.errors import (SelectionProviderNotFoundError,
                                       IDConflictError)


class SelectionService(HasTraits):
    """ The selection service connects selection providers and listeners.

    The selection service is a register of selection providers, i.e., objects
    that publish their current selection.

    Selections can be requested actively, by explicitly requesting the current
    selection in a provider (:meth:`get_selection(id)`), or passively by
    connecting selection listeners.
    """

    #### 'SelectionService' protocol ##########################################

    def add_selection_provider(self, provider):
        """ Add a selection provider.

        The provider is identified by its ID. If a provider with the same
        ID has been already registered, an :class:`~.IDConflictError`
        is raised.

        Arguments
        ---------
        provider -- ISelectionProvider
            The selection provider added to the internal registry.

        """
        if self.has_selection_provider(provider.id):
            raise IDConflictError(provider_id=provider.id)
        self._providers[provider.id] = provider

    def has_selection_provider(self, id):
        """ Has a provider with the given ID been registered? """
        return id in self._providers

    def remove_selection_provider(self, provider):
        """ Remove a selection provider.

        If the provider has not been registered, a
        :class:`~.SelectionProviderNotFoundError` is raised.

        Arguments
        ---------
        provider -- ISelectionProvider
            The selection provider added to the internal registry.
        """
        self._raise_if_not_registered(provider.id)
        del self._providers[provider.id]

    def get_selection(self, id):
        """ Return the current selection of the provider with the given ID.

        If a provider with that ID has not been registered, a
        :class:`~.SelectionProviderNotFoundError` is raised.

        Arguments
        ---------
        id -- str
            The selection provider ID.

        Returns
        -------
        selection -- ISelection
            The current selection of the provider.
        """
        self._raise_if_not_registered(id)
        provider = self._providers[id]
        return provider.get_selection()

    #### Private protocol #####################################################

    _providers = Dict()

    def _raise_if_not_registered(self, id):
        if not self.has_selection_provider(id):
            raise SelectionProviderNotFoundError(provider_id=id)
