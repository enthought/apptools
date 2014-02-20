from traits.testing.unittest_tools import unittest

from apptools.selection.api import ListSelection


class TestListSelection(unittest.TestCase):

    def test_list_selection(self):
        all_items = ['a', 'b', 'c', 'd']
        selected = ['d', 'b']
        list_selection = ListSelection(source_id='foo', selected=selected,
                                       all_items=all_items)

        self.assertEqual(list_selection.items, selected)
        self.assertEqual(list_selection.indices, [3, 1])


if __name__ == '__main__':
    unittest.main()
