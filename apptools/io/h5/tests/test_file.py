import os

import numpy as np
from numpy import testing
import tables

from ..file import H5File
from ..dict_node import H5DictNode
from ..table_node import H5TableNode
from .utils import open_h5file, temp_h5_file


H5_TEST_FILE = '_temp_test_filt.h5'


def teardown():
    try:
        os.remove(H5_TEST_FILE)
    except OSError:
        pass


def test_create_array():
    array = np.arange(3)
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5array = h5.create_array('/array', array)
        # Test returned array
        testing.assert_allclose(h5array, array)
        # Test stored array
        testing.assert_allclose(h5['/array'], array)


def test_create_plain_array():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5array = h5.create_array('/array', np.arange(3), chunked=False)
        assert isinstance(h5array, tables.Array)
        assert not isinstance(h5array, tables.CArray)


def test_create_chunked_array():
    array = np.arange(3, dtype=np.uint8)
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5array = h5.create_array('/array', array, chunked=True)
        testing.assert_allclose(h5array, array)
        assert isinstance(h5array, tables.CArray)


def test_shape_and_dtype():
    array = np.ones((3, 4), dtype=np.uint8)
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        for node, chunked in (('/array', False), ('/carray', True)):
            h5array = h5.create_array(node, array.shape, dtype=array.dtype,
                                      chunked=chunked)
            assert h5array.dtype == array.dtype
            assert h5array.shape == array.shape


def test_create_duplicate_array_raises():
    array = np.arange(3)
    with open_h5file(H5_TEST_FILE, mode='w', delete_existing=False) as h5:
        h5.create_array('/array', array)
        testing.assert_raises(ValueError, h5.create_array, '/array', array)


def test_delete_existing():
    old_array = np.arange(3)
    new_array = np.ones(5)
    with open_h5file(H5_TEST_FILE, mode='w', delete_existing=True) as h5:
        h5.create_array('/array', old_array)
        # New array with the same node name should delete old array
        h5.create_array('/array', new_array)
        testing.assert_allclose(h5['/array'], new_array)


def test_remove_node():
    with open_h5file(H5_TEST_FILE, mode='w', delete_existing=True) as h5:
        h5.create_array('/array', np.arange(3))
        assert '/array' in h5
        h5.remove_node('/array')
        assert '/array' not in h5


def test_read_mode_raises_on_nonexistent_file():
    cm = open_h5file('_nonexistent_.h5', mode='r')
    testing.assert_raises(IOError, cm.__enter__)
    cm = open_h5file('_nonexistent_.h5', mode='r+')
    testing.assert_raises(IOError, cm.__enter__)


def test_cleanup():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5_pytables = h5._h5  # This reference gets deleted on close
    assert not h5_pytables.isopen


def test_create_group():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5.create_group('/group')
        assert '/group' in h5


def test_split_path():
    path, node = H5File.split_path('/')
    assert path == '/'
    assert node == ''

    path, node = H5File.split_path('/node')
    assert path == '/'
    assert node == 'node'

    path, node = H5File.split_path('/group/node')
    assert path == '/group'
    assert node == 'node'


def test_join_path():
    path = H5File.join_path('/', 'a', 'b', 'c')
    assert path == '/a/b/c'

    path = H5File.join_path('a', 'b/c')
    assert path == '/a/b/c'

    path = H5File.join_path('a', '/b', '/c')
    assert path == '/a/b/c'


def test_auto_groups():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5.auto_groups = True
        h5.create_array('/group/array', np.arange(3))
        assert '/group/array' in h5


def test_auto_groups_deep():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5.auto_groups = True
        h5.create_array('/group1/group2/array', np.arange(3))
        assert '/group1/group2/array' in h5


def test_groups():
    array = np.arange(3)
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5.create_array('/a/b/array', array)
        group_a = h5['/a']
        # Check that __contains__ works for groups
        assert 'b' in group_a
        assert 'b/array' in group_a
        group_b = group_a['b']
        # Check that __contains__ works for arrays
        assert 'array' in group_b
        testing.assert_allclose(group_b['array'], array)
        testing.assert_allclose(group_a['b/array'], array)


def test_group_attributes():
    value_1 = 'foo'
    value_2 = 'bar'
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5['/'].attrs['name'] = value_1
        assert h5['/'].attrs['name'] == value_1
        group = h5['/']

        # Make sure changes to the attribute consistent
        group._h5_group._v_attrs['name'] = value_2
        assert group.attrs['name'] == value_2


def test_attribute_translation():
    value_1 = (1, 2, 3)
    value_1_array = np.array(value_1)
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5['/'].attrs['name'] = value_1
        assert isinstance(h5['/'].attrs['name'], np.ndarray)
        testing.assert_allclose(h5['/'].attrs['name'], value_1_array)


def test_get_attribute():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        attrs = h5['/'].attrs
        attrs['name'] = 'hello'
        assert attrs.get('name') == attrs['name']


def test_get_attribute_default():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        assert h5['/'].attrs.get('missing', 'null') == 'null'


def test_bad_node_name():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        testing.assert_raises(ValueError, h5.create_array,
                              '/attrs', np.zeros(3))


def test_bad_group_name():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        testing.assert_raises(ValueError, h5.create_array,
                              '/attrs/array', np.zeros(3))


def test_create_dict():
    data = {'a': 1}
    with temp_h5_file() as h5:
        h5.create_dict('/dict', data)
        assert isinstance(h5['/dict'], H5DictNode)
        assert h5['/dict']['a'] == 1


def test_create_table():
    description = [('foo', 'int'), ('bar', 'float')]
    with temp_h5_file() as h5:
        h5.create_table('/table', description)
        tab = h5['/table']
        assert isinstance(tab, H5TableNode)
        tab.append({'foo': (1,), 'bar': (np.pi,)})
        assert tab.ix[0][0] == 1
        assert tab.ix[0][1] == np.pi

        h5.remove_node('/table')
        assert '/table' not in h5


if __name__ == '__main__':
    testing.run_module_suite()
