# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
import unittest

from traits.api import Any, Event, HasTraits, List, provides, Str

from apptools.selection.api import (
    IDConflictError,
    ISelection,
    ISelectionProvider,
    ListenerNotConnectedError,
    ListSelection,
    ProviderNotRegisteredError,
    SelectionService,
)


@provides(ISelection)
class BogusSelection(HasTraits):

    provider_id = Str

    # Some content to check that two selections are the same
    content = Any

    def is_empty(self):
        """ Is the selection empty? """
        return False


@provides(ISelectionProvider)
class BogusSelectionProvider(HasTraits):

    #### 'ISelectionProvider' protocol ########################################

    provider_id = Str

    selection = Event

    def get_selection(self):
        return BogusSelection(
            provider_id=self.provider_id, content="get_selection"
        )

    def set_selection(self, items, ignore_missing=False):
        pass

    #### 'BogusSelectionProvider' protocol ####################################

    def trigger_selection(self, content):
        self.selection = BogusSelection(
            provider_id=self.provider_id, content=content
        )


class BogusListener(HasTraits):
    selections = List

    def on_selection_changed(self, selection):
        self.selections.append(selection)


@provides(ISelectionProvider)
class SimpleListProvider(HasTraits):

    #### 'ISelectionProvider' protocol ########################################

    provider_id = Str("test.simple_list_provider")

    selection = Event

    def get_selection(self):
        selection = ListSelection.from_available_items(
            provider_id=self.provider_id,
            selected=self._selected,
            all_items=self.items,
        )
        return selection

    def set_selection(self, items, ignore_missing=False):
        selected = [x for x in items if x in self.items]
        if not ignore_missing and len(selected) < len(items):
            raise ValueError()
        self._selected = selected

    #### 'SimpleListProvider' protocol ########################################

    items = List

    _selected = List


class TestSelectionService(unittest.TestCase):
    def test_add_selection_provider(self):
        service = SelectionService()
        provider = BogusSelectionProvider()

        service.add_selection_provider(provider)
        self.assertTrue(service.has_selection_provider(provider.provider_id))

    def test_add_selection_id_conflict(self):
        service = SelectionService()

        provider_id = "Foo"
        provider = BogusSelectionProvider(provider_id=provider_id)
        another_provider = BogusSelectionProvider(provider_id=provider_id)

        service.add_selection_provider(provider)
        with self.assertRaises(IDConflictError):
            service.add_selection_provider(another_provider)

    def test_remove_selection_provider(self):
        service = SelectionService()
        provider = BogusSelectionProvider(provider_id="Bogus")

        service.add_selection_provider(provider)
        service.remove_selection_provider(provider)
        self.assertFalse(service.has_selection_provider(provider.provider_id))

        with self.assertRaises(ProviderNotRegisteredError):
            service.remove_selection_provider(provider)

    def test_get_selection(self):
        service = SelectionService()
        provider_id = "Bogus"
        provider = BogusSelectionProvider(provider_id=provider_id)
        service.add_selection_provider(provider)

        selection = service.get_selection(provider_id)

        self.assertIsInstance(selection, ISelection)
        self.assertEqual(selection.provider_id, provider.provider_id)

    def test_get_selection_id_not_registered(self):
        service = SelectionService()

        with self.assertRaises(ProviderNotRegisteredError):
            service.get_selection("not-registered")

    def test_connect_listener(self):
        service = SelectionService()
        provider_id = "Bogus"
        provider = BogusSelectionProvider(provider_id=provider_id)
        service.add_selection_provider(provider)

        listener = BogusListener()
        service.connect_selection_listener(
            provider_id, listener.on_selection_changed
        )

        content = [1, 2, 3]
        provider.trigger_selection(content)

        selections = listener.selections
        self.assertEqual(len(selections), 1)
        self.assertEqual(selections[0].provider_id, provider.provider_id)
        self.assertEqual(selections[0].content, content)

    def test_connect_listener_then_add_remove_provider(self):
        service = SelectionService()
        provider_id = "Bogus"

        # Connect listener before provider is registered.
        listener = BogusListener()
        service.connect_selection_listener(
            provider_id, listener.on_selection_changed
        )

        # When the provider is first added, the listener should receive the
        # initial selection (as returned by provider.get_selection)
        provider = BogusSelectionProvider(provider_id=provider_id)
        expected = provider.get_selection()
        service.add_selection_provider(provider)

        selections = listener.selections
        self.assertEqual(len(selections), 1)
        self.assertEqual(selections[-1].content, expected.content)

        # When the provider changes the selection, the event arrive as usual.
        content = [1, 2, 3]
        provider.trigger_selection(content)

        self.assertEqual(len(selections), 2)
        self.assertEqual(selections[-1].content, content)

        # When we un-register the provider, a change in selection does not
        # generate a callback.
        service.remove_selection_provider(provider)
        provider.trigger_selection(content)
        self.assertEqual(len(selections), 2)

        # Finally, we register again and get the current selection.
        service.add_selection_provider(provider)
        self.assertEqual(len(selections), 3)
        self.assertEqual(selections[-1].content, expected.content)

    def test_disconnect_listener(self):
        service = SelectionService()
        provider_id = "Bogus"
        provider = BogusSelectionProvider(provider_id=provider_id)
        service.add_selection_provider(provider)

        listener = BogusListener()
        service.connect_selection_listener(
            provider_id, listener.on_selection_changed
        )
        service.disconnect_selection_listener(
            provider_id, listener.on_selection_changed
        )

        provider.trigger_selection([1, 2, 3])

        self.assertEqual(len(listener.selections), 0)

    def test_disconnect_unknown_listener(self):
        service = SelectionService()
        provider_id = "Bogus"
        provider = BogusSelectionProvider(provider_id=provider_id)
        service.add_selection_provider(provider)

        # First case: there are listeners to a provider, but not the one we
        # pass to the disconnect method
        listener_1 = BogusListener()
        service.connect_selection_listener(
            provider_id, listener_1.on_selection_changed
        )

        listener_2 = BogusListener()
        with self.assertRaises(ListenerNotConnectedError):
            service.disconnect_selection_listener(
                provider_id, listener_2.on_selection_changed
            )

        # Second case: there is no listener connected to the ID
        with self.assertRaises(ListenerNotConnectedError):
            service.disconnect_selection_listener(
                "does-not-exists", listener_2.on_selection_changed
            )

    def test_set_selection(self):
        service = SelectionService()
        provider = SimpleListProvider(items=list(range(10)))
        service.add_selection_provider(provider)

        provider_id = provider.provider_id
        selection = service.get_selection(provider_id)
        self.assertTrue(selection.is_empty())

        new_selection = [5, 6, 3]
        service.set_selection(provider_id, new_selection)

        selection = service.get_selection(provider_id)
        self.assertFalse(selection.is_empty())

        # We can't assume that the order of the items in the selection we set
        # remains stable.
        self.assertEqual(selection.items, new_selection)
        self.assertEqual(selection.indices, selection.items)

    def test_selection_id_not_registered(self):
        service = SelectionService()

        with self.assertRaises(ProviderNotRegisteredError):
            service.set_selection(provider_id="not-existent", items=[])

    def test_ignore_missing(self):
        # What we are really testing here is that the selection service
        # passes the keyword argument to the selection provider. It's the
        # selection provider responsibility to ignore missing elements, or
        # raise an exception.

        service = SelectionService()
        provider = SimpleListProvider(items=list(range(10)))
        service.add_selection_provider(provider)

        new_selection = [0, 11, 1]
        provider_id = provider.provider_id
        service.set_selection(provider_id, new_selection, ignore_missing=True)

        selection = service.get_selection(provider_id)
        self.assertFalse(selection.is_empty())
        self.assertEqual(selection.items, [0, 1])

        new_selection = [0, 11, 1]
        with self.assertRaises(ValueError):
            service.set_selection(
                provider_id, new_selection, ignore_missing=False
            )
