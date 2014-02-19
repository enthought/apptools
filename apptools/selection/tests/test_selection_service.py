from traits.api import HasTraits, Instance, provides, Str
from traits.testing.unittest_tools import unittest

from apptools.selection.api import (IDConflictError, ISelection,
    ISelectionProvider, SelectionProviderNotFoundError, SelectionService)


@provides(ISelection)
class BogusSelection(HasTraits):

    # Provider that created the selection.
    from_ = Instance(ISelectionProvider)

    def is_empty(self):
        """ Is the selection empty? """
        return False


@provides(ISelectionProvider)
class BogusSelectionProvider(HasTraits):

    id = Str

    def get_selection(self):
        return BogusSelection(from_=self)


class TestSelectionService(unittest.TestCase):

    def test_add_selection_provider(self):
        service = SelectionService()
        provider = BogusSelectionProvider()

        service.add_selection_provider(provider)
        self.assertTrue(service.has_selection_provider(provider.id))

    def test_add_selection_id_conflict(self):
        service = SelectionService()

        provider_id = 'Foo'
        provider = BogusSelectionProvider(id=provider_id)
        another_provider = BogusSelectionProvider(id=provider_id)

        service.add_selection_provider(provider)
        with self.assertRaises(IDConflictError):
            service.add_selection_provider(another_provider)

    def test_remove_selection_provider(self):
        service = SelectionService()
        provider = BogusSelectionProvider(id='Bogus')

        service.add_selection_provider(provider)
        service.remove_selection_provider(provider)
        self.assertFalse(service.has_selection_provider(provider.id))

        with self.assertRaises(SelectionProviderNotFoundError):
            service.remove_selection_provider(provider)

    def test_get_selection(self):
        service = SelectionService()
        provider_id = 'Bogus'
        provider = BogusSelectionProvider(id=provider_id)
        service.add_selection_provider(provider)

        selection = service.get_selection(provider_id)

        self.assertIsInstance(selection, ISelection)
        self.assertEqual(selection.from_, provider)

    def test_get_selection_id_not_registered(self):
        service = SelectionService()

        with self.assertRaises(SelectionProviderNotFoundError):
            service.get_selection('not-registered')


if __name__ == '__main__':
    unittest.main()
