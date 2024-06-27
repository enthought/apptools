# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
from traits.api import Dict, HasTraits

from apptools.selection.errors import (
    ProviderNotRegisteredError,
    IDConflictError,
    ListenerNotConnectedError,
)


class SelectionService(HasTraits):
    """The selection service connects selection providers and listeners.

    The selection service is a register of selection providers, i.e., objects
    that publish their current selection.

    Selections can be requested actively, by explicitly requesting the current
    selection in a provider (:meth:`get_selection(id)`), or passively by
    connecting selection listeners.
    """

    #### 'SelectionService' protocol ##########################################

    def add_selection_provider(self, provider):
        """Add a selection provider.

        The provider is identified by its ID. If a provider with the same
        ID has been already registered, an :class:`~.IDConflictError`
        is raised.

        Arguments:
            provider -- ISelectionProvider
                The selection provider added to the internal registry.

        """
        provider_id = provider.provider_id
        if self.has_selection_provider(provider_id):
            raise IDConflictError(provider_id=provider_id)

        self._providers[provider_id] = provider

        if provider_id in self._listeners:
            self._connect_all_listeners(provider_id)

    def has_selection_provider(self, provider_id):
        """ Has a provider with the given ID been registered? """
        return provider_id in self._providers

    def remove_selection_provider(self, provider):
        """Remove a selection provider.

        If the provider has not been registered, a
        :class:`~.ProviderNotRegisteredError` is raised.

        Arguments:
            provider -- ISelectionProvider
                The selection provider added to the internal registry.
        """
        provider_id = provider.provider_id
        self._raise_if_not_registered(provider_id)

        if provider_id in self._listeners:
            self._disconnect_all_listeners(provider_id)

        del self._providers[provider_id]

    def get_selection(self, provider_id):
        """Return the current selection of the provider with the given ID.

        If a provider with that ID has not been registered, a
        :class:`~.ProviderNotRegisteredError` is raised.

        Arguments:
            provider_id -- str
                The selection provider ID.

        Returns:
            selection -- ISelection
                The current selection of the provider.
        """
        self._raise_if_not_registered(provider_id)
        provider = self._providers[provider_id]
        return provider.get_selection()

    def set_selection(self, provider_id, items, ignore_missing=False):
        """Set the current selection in a provider to the given items.

        If a provider with the given ID has not been registered, a
        :class:`~.ProviderNotRegisteredError` is raised.

        If ``ignore_missing`` is ``True``, items that are not available in the
        selection provider are silently ignored. If it is ``False`` (default),
        a :class:`ValueError` should be raised.

        Arguments:
            provider_id -- str
                The selection provider ID.

            items -- list
                List of items to be selected.

            ignore_missing -- bool
                If ``False`` (default), the provider raises an exception if any
                of the items in ``items`` is not available to be selected.
                Otherwise, missing elements are silently ignored, and the rest
                is selected.
        """
        self._raise_if_not_registered(provider_id)
        provider = self._providers[provider_id]
        return provider.set_selection(items, ignore_missing=ignore_missing)

    def connect_selection_listener(self, provider_id, func):
        """Connect a listener to selection events from a specific provider.

        The signature if the listener callback is ``func(i_selection)``.
        The listener is called:

        1) When a provider with the given ID is registered, with its initial
           selection as argument, or

        2) whenever the provider fires a selection event.

        It is perfectly valid to connect a listener before a provider with the
        given ID is registered. The listener will remain connected even if
        the provider is repeatedly connected and disconnected.

        Arguments:
            provider_id -- str
                The selection provider ID.
            func -- callable(i_selection)
                A callable object that is notified when the selection changes.
        """
        self._listeners.setdefault(provider_id, [])
        self._listeners[provider_id].append(func)

        if self.has_selection_provider(provider_id):
            self._toggle_listener(provider_id, func, remove=False)

    def disconnect_selection_listener(self, provider_id, func):
        """Disconnect a listener from a specific provider.

        Arguments:
            provider_id -- str
                The selection provider ID.
            func -- callable(provider_id, i_selection)
                A callable object that is notified when the selection changes.
        """

        if self.has_selection_provider(provider_id):
            self._toggle_listener(provider_id, func, remove=True)

        try:
            self._listeners[provider_id].remove(func)
        except (ValueError, KeyError):
            raise ListenerNotConnectedError(
                provider_id=provider_id, listener=func
            )

    #### Private protocol #####################################################

    _listeners = Dict()

    _providers = Dict()

    def _toggle_listener(self, provider_id, func, remove):
        provider = self._providers[provider_id]
        provider.on_trait_change(func, "selection", remove=remove)

    def _connect_all_listeners(self, provider_id):
        """Connect all listeners connected to a provider.

        As soon as they are connected, they receive the initial selection.
        """
        provider = self._providers[provider_id]
        selection = provider.get_selection()
        for func in self._listeners[provider_id]:
            self._toggle_listener(provider_id, func, remove=False)
            # FIXME: make this robust to notifications that raise exceptions.
            # Can we send the error to the traits exception hook?
            func(selection)

    def _disconnect_all_listeners(self, provider_id):
        for func in self._listeners[provider_id]:
            self._toggle_listener(provider_id, func, remove=True)

    def _raise_if_not_registered(self, provider_id):
        if not self.has_selection_provider(provider_id):
            raise ProviderNotRegisteredError(provider_id=provider_id)
