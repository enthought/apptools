import numpy

from traits.testing.unittest_tools import unittest

from apptools.selection.api import ListSelection


class TestListSelection(unittest.TestCase):

    def test_list_selection(self):
        all_items = ['a', 'b', 'c', 'd']
        selected = ['d', 'b']
        list_selection = ListSelection.from_available_items(
            provider_id='foo', selected=selected, all_items=all_items)

        self.assertEqual(list_selection.items, selected)
        self.assertEqual(list_selection.indices, [3, 1])

    def test_list_selection_of_sequence_items(self):
        all_items = [['a', 'b'], ['c', 'd'], ['e', 'f']]
        selected = [all_items[2], all_items[1]]
        list_selection = ListSelection.from_available_items(
            provider_id='foo', selected=selected, all_items=all_items)

        self.assertEqual(list_selection.items, selected)
        self.assertEqual(list_selection.indices, [2, 1])

    def test_list_selection_of_numpy_array_items(self):
        data = numpy.arange(10)
        all_items = [data, data + 10, data + 30]
        selected = [all_items[0], all_items[2]]

        list_selection = ListSelection.from_available_items(
            provider_id='foo', selected=selected, all_items=all_items)

        self.assertEqual(list_selection.items, selected)
        self.assertEqual(list_selection.indices, [0, 2])

    def test_list_selection_with_invalid_selected_items(self):
        data = numpy.arange(10)
        all_items = [data, data + 10, data + 30]
        selected = [data-10, ]

        with self.assertRaises(ValueError):
            ListSelection.from_available_items(
                provider_id='foo', selected=selected, all_items=all_items)


if __name__ == '__main__':
    unittest.main()
