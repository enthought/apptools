from traits.api import HasTraits, Instance, provides, Str
from traits.testing.unittest_tools import unittest

from apptools.selection.api import (ISelection, ISelectionProvider,
    SelectionProviderNotFoundError, SelectionService)


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
        self.assertTrue(service.has_selection_provider(provider))

    def test_remove_selection_provider(self):
        service = SelectionService()
        provider = BogusSelectionProvider(id='Bogus')

        service.add_selection_provider(provider)
        service.remove_selection_provider(provider)
        self.assertFalse(service.has_selection_provider(provider))

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



# Test ID conflict
# Test empty ID
# Test get_selection with not-exitent ID

if __name__ == '__main__':
    unittest.main()
