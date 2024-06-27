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

from apptools._testing.optional_dependencies import (
    numpy as np,
    tables,
    requires_numpy,
    requires_tables,
)

if np is not None and tables is not None:
    from ..dict_node import H5DictNode
    from .utils import open_h5file, temp_h5_file, temp_file


NODE = "/dict_node"


@requires_tables
@requires_numpy
class DictNodeTestCase(unittest.TestCase):
    def test_create(self):
        with temp_h5_file() as h5:
            h5dict = H5DictNode.add_to_h5file(h5, NODE)
            h5dict["a"] = 1
            h5dict["b"] = 2

            assert h5dict["a"] == 1
            assert h5dict["b"] == 2

    def test_is_dict_node(self):
        with temp_h5_file() as h5:
            node = h5.create_dict(NODE, {})
            assert H5DictNode.is_dict_node(node._h5_group)

    def test_is_not_dict_node(self):
        with temp_h5_file() as h5:
            node = h5.create_group(NODE)
            assert not H5DictNode.is_dict_node(node)
            assert not H5DictNode.is_dict_node(node._h5_group)

    def test_create_with_data(self):
        with temp_h5_file() as h5:
            data = {"a": 10}

            h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
            assert h5dict["a"] == 10

    def test_create_with_array_data(self):
        foo = np.arange(100)
        bar = np.arange(150)

        with temp_h5_file() as h5:
            data = {"a": 10, "foo": foo, "bar": bar}

            h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
            assert h5dict["a"] == 10
            np.testing.assert_allclose(h5dict["foo"], foo)
            np.testing.assert_allclose(h5dict["bar"], bar)

    def test_load_saved_dict_node(self):
        with temp_file() as filename:
            # Write data to new dict node and close.
            with open_h5file(filename, "w") as h5:
                h5dict = H5DictNode.add_to_h5file(h5, NODE)
                h5dict["a"] = 1

            # Read dict node and make sure the data was saved.
            with open_h5file(filename, mode="r+") as h5:
                h5dict = h5[NODE]
                assert h5dict["a"] == 1
                # Change data for next test
                h5dict["a"] = 2

            # Check that data is modified by the previous write.
            with open_h5file(filename) as h5:
                h5dict = h5[NODE]
                assert h5dict["a"] == 2

    def test_load_saved_dict_node_with_array(self):
        arr = np.arange(100)
        arr1 = np.arange(200)

        with temp_file() as filename:
            # Write data to new dict node and close.
            with open_h5file(filename, "w") as h5:
                h5dict = H5DictNode.add_to_h5file(h5, NODE)
                h5dict["arr"] = arr

            # Read dict node and make sure the data was saved.
            with open_h5file(filename, mode="r+") as h5:
                h5dict = h5[NODE]
                np.testing.assert_allclose(h5dict["arr"], arr)
                # Change data for next test
                h5dict["arr"] = arr1
                h5dict["arr_old"] = arr

            # Check that data is modified by the previous write.
            with open_h5file(filename) as h5:
                h5dict = h5[NODE]
                np.testing.assert_allclose(h5dict["arr"], arr1)
                np.testing.assert_allclose(h5dict["arr_old"], arr)
                # Make sure that arrays come back as arrays
                assert isinstance(h5dict["arr"], np.ndarray)
                assert isinstance(h5dict["arr_old"], np.ndarray)

    def test_keys(self):
        with temp_h5_file() as h5:
            keys = set(("hello", "world", "baz1"))
            data = dict((n, 1) for n in keys)
            h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
            assert set(h5dict.keys()) == keys

    def test_delete_item(self):
        with temp_h5_file() as h5:
            data = dict(a=10)
            h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
            del h5dict["a"]
            assert "a" not in h5dict

    def test_delete_array(self):
        with temp_h5_file() as h5:
            data = dict(a=np.arange(10))
            h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
            del h5dict["a"]
            assert "a" not in h5dict
            assert "a" not in h5[NODE]

    def test_auto_flush(self):
        with temp_h5_file() as h5:
            data = dict(a=1)
            h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
            # Overwrite existing data, which should get written to disk.
            new_data = dict(b=2)
            h5dict.data = new_data
            # Load data from disk to check that data was automatically flushed.
            h5dict_from_disk = h5[NODE]
            assert "a" not in h5dict_from_disk
            assert h5dict_from_disk["b"] == 2

    def test_auto_flush_off(self):
        with temp_h5_file() as h5:
            data = dict(a=1)
            h5dict = H5DictNode.add_to_h5file(h5, NODE, data, auto_flush=False)
            # Overwrite existing data, but don't write to disk.
            new_data = dict(b=2)
            h5dict.data = new_data
            # Load data from disk to check that it's unchanged.
            h5dict_from_disk = h5[NODE]
            assert h5dict_from_disk["a"] == 1
            assert "b" not in h5dict_from_disk
            # Manually flush, and check that data was written
            h5dict.flush()
            h5dict_from_disk = h5[NODE]
            assert "a" not in h5dict_from_disk
            assert h5dict_from_disk["b"] == 2

    def test_undefined_key(self):
        with temp_h5_file() as h5:
            data = dict(a="int")
            h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
            with self.assertRaises(KeyError):
                del h5dict["b"]

    def test_basic_dtypes(self):
        with temp_h5_file() as h5:
            data = dict(a_int=1, a_float=1.0, a_str="abc")
            h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
            assert isinstance(h5dict["a_int"], int)
            assert isinstance(h5dict["a_float"], float)
            assert isinstance(h5dict["a_str"], str)

    def test_mixed_type_list(self):
        with temp_h5_file() as h5:
            data = dict(a=[1, 1.0, "abc"])
            h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
            for value, dtype in zip(
                h5dict["a"], (int, float, str)
            ):
                assert isinstance(value, dtype)

    def test_dict(self):
        with temp_h5_file() as h5:
            data = dict(a=dict(b=1, c=2))
            h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
            sub_dict = h5dict["a"]
            assert sub_dict["b"] == 1
            assert sub_dict["c"] == 2

    def test_wrap_self_raises_error(self):
        with temp_h5_file() as h5:
            H5DictNode.add_to_h5file(h5, NODE)
            node = h5[NODE]
            with self.assertRaises(AssertionError):
                H5DictNode(node)
