import numpy as np
from numpy.testing import raises, assert_allclose
import six

from ..dict_node import H5DictNode
from .utils import open_h5file, temp_h5_file, temp_file


NODE = '/dict_node'


def test_create():
    with temp_h5_file() as h5:
        h5dict = H5DictNode.add_to_h5file(h5, NODE)
        h5dict['a'] = 1
        h5dict['b'] = 2

        assert h5dict['a'] == 1
        assert h5dict['b'] == 2


def test_is_dict_node():
    with temp_h5_file() as h5:
        node = h5.create_dict(NODE, {})
        assert H5DictNode.is_dict_node(node._h5_group)


def test_is_not_dict_node():
    with temp_h5_file() as h5:
        node = h5.create_group(NODE)
        assert not H5DictNode.is_dict_node(node)
        assert not H5DictNode.is_dict_node(node._h5_group)


def test_create_with_data():
    with temp_h5_file() as h5:
        data = {'a': 10}

        h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
        assert h5dict['a'] == 10


def test_create_with_array_data():
    foo = np.arange(100)
    bar = np.arange(150)

    with temp_h5_file() as h5:
        data = {'a': 10, 'foo': foo, 'bar': bar}

        h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
        assert h5dict['a'] == 10
        assert_allclose(h5dict['foo'], foo)
        assert_allclose(h5dict['bar'], bar)


def test_load_saved_dict_node():
    with temp_file() as filename:
        # Write data to new dict node and close.
        with open_h5file(filename, 'w') as h5:
            h5dict = H5DictNode.add_to_h5file(h5, NODE)
            h5dict['a'] = 1

        # Read dict node and make sure the data was saved.
        with open_h5file(filename, mode='r+') as h5:
            h5dict = h5[NODE]
            assert h5dict['a'] == 1
            # Change data for next test
            h5dict['a'] = 2

        # Check that data is modified by the previous write.
        with open_h5file(filename) as h5:
            h5dict = h5[NODE]
            assert h5dict['a'] == 2


def test_load_saved_dict_node_with_array():
    arr = np.arange(100)
    arr1 = np.arange(200)

    with temp_file() as filename:
        # Write data to new dict node and close.
        with open_h5file(filename, 'w') as h5:
            h5dict = H5DictNode.add_to_h5file(h5, NODE)
            h5dict['arr'] = arr

        # Read dict node and make sure the data was saved.
        with open_h5file(filename, mode='r+') as h5:
            h5dict = h5[NODE]
            assert_allclose(h5dict['arr'], arr)
            # Change data for next test
            h5dict['arr'] = arr1
            h5dict['arr_old'] = arr

        # Check that data is modified by the previous write.
        with open_h5file(filename) as h5:
            h5dict = h5[NODE]
            assert_allclose(h5dict['arr'], arr1)
            assert_allclose(h5dict['arr_old'], arr)
            # Make sure that arrays come back as arrays
            assert isinstance(h5dict['arr'], np.ndarray)
            assert isinstance(h5dict['arr_old'], np.ndarray)


def test_keys():
    with temp_h5_file() as h5:
        keys = set(('hello', 'world', 'baz1'))
        data = dict((n, 1) for n in keys)
        h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
        assert set(h5dict.keys()) == keys


def test_delete_item():
    with temp_h5_file() as h5:
        data = dict(a=10)
        h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
        del h5dict['a']
        assert 'a' not in h5dict


def test_delete_array():
    with temp_h5_file() as h5:
        data = dict(a=np.arange(10))
        h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
        del h5dict['a']
        assert 'a' not in h5dict
        assert 'a' not in h5[NODE]


def test_auto_flush():
    with temp_h5_file() as h5:
        data = dict(a=1)
        h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
        # Overwrite existing data, which should get written to disk.
        new_data = dict(b=2)
        h5dict.data = new_data
        # Load data from disk to check that data was automatically flushed.
        h5dict_from_disk = h5[NODE]
        assert 'a' not in h5dict_from_disk
        assert h5dict_from_disk['b'] == 2


def test_auto_flush_off():
    with temp_h5_file() as h5:
        data = dict(a=1)
        h5dict = H5DictNode.add_to_h5file(h5, NODE, data, auto_flush=False)
        # Overwrite existing data, but don't write to disk.
        new_data = dict(b=2)
        h5dict.data = new_data
        # Load data from disk to check that it's unchanged.
        h5dict_from_disk = h5[NODE]
        assert h5dict_from_disk['a'] == 1
        assert 'b' not in h5dict_from_disk
        # Manually flush, and check that data was written
        h5dict.flush()
        h5dict_from_disk = h5[NODE]
        assert 'a' not in h5dict_from_disk
        assert h5dict_from_disk['b'] == 2


@raises(KeyError)
def test_undefined_key():
    with temp_h5_file() as h5:
        data = dict(a='int')
        h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
        del h5dict['b']


def test_basic_dtypes():
    with temp_h5_file() as h5:
        data = dict(a_int=1, a_float=1.0, a_str='abc')
        h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
        assert isinstance(h5dict['a_int'], int)
        assert isinstance(h5dict['a_float'], float)
        assert isinstance(h5dict['a_str'], six.string_types)


def test_mixed_type_list():
    with temp_h5_file() as h5:
        data = dict(a=[1, 1.0, 'abc'])
        h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
        for value, dtype in zip(h5dict['a'], (int, float, six.string_types)):
            assert isinstance(value, dtype)


def test_dict():
    with temp_h5_file() as h5:
        data = dict(a=dict(b=1, c=2))
        h5dict = H5DictNode.add_to_h5file(h5, NODE, data)
        sub_dict = h5dict['a']
        assert sub_dict['b'] == 1
        assert sub_dict['c'] == 2


@raises(AssertionError)
def test_wrap_self_raises_error():
    with temp_h5_file() as h5:
        H5DictNode.add_to_h5file(h5, NODE)
        node = h5[NODE]
        H5DictNode(node)


if __name__ == '__main__':
    from numpy import testing
    testing.run_module_suite()
