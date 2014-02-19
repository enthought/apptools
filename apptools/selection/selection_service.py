from traits.api import Dict, HasTraits

from apptools.selection.errors import (ProviderNotRegisteredError,
    IDConflictError, ListenerNotConnectedError)


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

        if self._listeners.has_key(provider.id):
            self._connect_all_listeners(provider.id)

    def has_selection_provider(self, id):
        """ Has a provider with the given ID been registered? """
        return id in self._providers

    def remove_selection_provider(self, provider):
        """ Remove a selection provider.

        If the provider has not been registered, a
        :class:`~.ProviderNotRegisteredError` is raised.

        Arguments
        ---------
        provider -- ISelectionProvider
            The selection provider added to the internal registry.
        """
        self._raise_if_not_registered(provider.id)

        if self._listeners.has_key(provider.id):
            self._disconnect_all_listeners(provider.id)

        del self._providers[provider.id]

    def get_selection(self, id):
        """ Return the current selection of the provider with the given ID.

        If a provider with that ID has not been registered, a
        :class:`~.ProviderNotRegisteredError` is raised.

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

    def connect_selection_listener(self, id, func):
        """ Connect a listener to selection events from a specific provider.

        The signature if the listener callback is ``func(id, i_selection)``.
        The listener is called:
        1) When a provider with the given ID is registered, with its initial
           selection as argument, or
        2) whenever the provider fires a selection event.

        It is perfectly valid to connect a listener before a provider with the
        given ID is registered. The listener will remain connected even if
        the provider is repeatedly connected and disconnected.

        Arguments
        ---------
        id -- str
            The selection provider ID.
        func -- callable(id, i_selection)
            A callable object that is notified when the selection changes.
        """
        self._listeners.setdefault(id, [])
        self._listeners[id].append(func)

        if self.has_selection_provider(id):
            self._toggle_listener(id, func, remove=False)

    def disconnect_selection_listener(self, id, func):
        """ Disonnect a listener from a specific provider.

        Arguments
        ---------
        id -- str
            The selection provider ID.
        func -- callable(id, i_selection)
            A callable object that is notified when the selection changes.
        """

        if self.has_selection_provider(id):
            self._toggle_listener(id, func, remove=True)

        try:
            self._listeners[id].remove(func)
        except (ValueError, KeyError):
            raise ListenerNotConnectedError(provider_id=id, listener=func)

    #### Private protocol #####################################################

    _listeners = Dict()

    _providers = Dict()

    def _toggle_listener(self, provider_id, func, remove):
        provider = self._providers[provider_id]
        provider.on_trait_change(func, 'selection', remove=remove)

    def _connect_all_listeners(self, provider_id):
        provider = self._providers[provider_id]
        selection = provider.get_selection()
        for func in self._listeners[provider_id]:
            self._toggle_listener(provider_id, func, remove=False)
            func(provider_id, selection)

    def _disconnect_all_listeners(self, provider_id):
        provider = self._providers[provider_id]
        for func in self._listeners[provider_id]:
            self._toggle_listener(provider_id, func, remove=True)

    def _raise_if_not_registered(self, id):
        if not self.has_selection_provider(id):
            raise ProviderNotRegisteredError(provider_id=id)
