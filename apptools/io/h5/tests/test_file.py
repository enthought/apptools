import os
from contextlib import closing

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


def test_reopen():
    h5 = H5File(H5_TEST_FILE, mode='w')
    assert h5.is_open
    h5.close()
    assert not h5.is_open
    h5.open()
    assert h5.is_open
    h5.close()


def test_open_from_pytables_object():
    with closing(tables.File(H5_TEST_FILE, 'w')) as pyt_file:
        pyt_file.create_group('/', 'my_group')
        with open_h5file(pyt_file) as h5:
            assert '/my_group' in h5


def test_open_from_closed_pytables_object():
    with closing(tables.File(H5_TEST_FILE, 'w')) as pyt_file:
        pyt_file.create_group('/', 'my_group')
        pyt_file.close()
        with open_h5file(pyt_file) as h5:
            assert '/my_group' in h5


def test_create_array_with_H5File():
    array = np.arange(3)
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5array = h5.create_array('/array', array)
        # Test returned array
        testing.assert_allclose(h5array, array)
        # Test stored array
        testing.assert_allclose(h5['/array'], array)


def test_create_array_with_H5Group():
    array = np.arange(3)
    node_path = '/tardigrade/array'
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        group = h5.create_group('/tardigrade')
        h5array = group.create_array('array', array)
        # Test returned array
        testing.assert_allclose(h5array, array)
        # Test stored array
        testing.assert_allclose(h5[node_path], array)


def test_getitem_failure():
    array = np.arange(3)
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5.create_array('/array', array)
        testing.assert_raises(NameError, h5.__getitem__, '/not_there')


def test_iteritems():
    node_paths = ['/foo', '/bar', '/baz']
    array = np.arange(3)
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        for path in node_paths:
            h5.create_array(path, array)

        # We expect to see the root node when calling iteritems...
        node_paths.append('/')
        iter_paths = []

        # 2to3 converts the iteritems blindly to items which is incorrect,
        # so we resort to this ugliness.
        items = getattr(h5, 'iteritems')()
        for path, node in items:
            iter_paths.append(path)

    assert set(node_paths) == set(iter_paths)


def test_create_plain_array_with_H5File():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5array = h5.create_array('/array', np.arange(3), chunked=False)
        assert isinstance(h5array, tables.Array)
        assert not isinstance(h5array, tables.CArray)


def test_create_plain_array_with_H5Group():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5array = h5.root.create_array('/array', np.arange(3), chunked=False)
        assert isinstance(h5array, tables.Array)
        assert not isinstance(h5array, tables.CArray)


def test_create_chunked_array_with_H5File():
    array = np.arange(3, dtype=np.uint8)
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5array = h5.create_array('/array', array, chunked=True)
        testing.assert_allclose(h5array, array)
        assert isinstance(h5array, tables.CArray)


def test_create_chunked_array_with_H5Group():
    array = np.arange(3, dtype=np.uint8)
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5array = h5.root.create_array('/array', array, chunked=True)
        testing.assert_allclose(h5array, array)
        assert isinstance(h5array, tables.CArray)


def test_create_extendable_array_with_H5File():
    array = np.arange(3, dtype=np.uint8)
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5array = h5.create_array('/array', array, extendable=True)
        testing.assert_allclose(h5array, array)
        assert isinstance(h5array, tables.EArray)


def test_create_extendable_array_with_H5Group():
    array = np.arange(3, dtype=np.uint8)
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5array = h5.root.create_array('/array', array, extendable=True)
        testing.assert_allclose(h5array, array)
        assert isinstance(h5array, tables.EArray)


def test_str_and_repr():
    array = np.arange(3)
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5.create_array('/array', array)

        assert repr(h5) == repr(h5._h5)
        assert str(h5) == str(h5._h5)


def test_shape_and_dtype():
    array = np.ones((3, 4), dtype=np.uint8)
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        for node, chunked in (('/array', False), ('/carray', True)):
            h5array = h5.create_array(node, array.shape, dtype=array.dtype,
                                      chunked=chunked)
            assert h5array.dtype == array.dtype
            assert h5array.shape == array.shape


def test_shape_only_raises():
    shape = (3, 4)
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        testing.assert_raises(ValueError, h5.create_array, '/array', shape)


def test_create_duplicate_array_raises():
    array = np.arange(3)
    with open_h5file(H5_TEST_FILE, mode='w', delete_existing=False) as h5:
        h5.create_array('/array', array)
        testing.assert_raises(ValueError, h5.create_array, '/array', array)


def test_delete_existing_array_with_H5File():
    old_array = np.arange(3)
    new_array = np.ones(5)
    with open_h5file(H5_TEST_FILE, mode='w', delete_existing=True) as h5:
        h5.create_array('/array', old_array)
        # New array with the same node name should delete old array
        h5.create_array('/array', new_array)
        testing.assert_allclose(h5['/array'], new_array)


def test_delete_existing_array_with_H5Group():
    old_array = np.arange(3)
    new_array = np.ones(5)
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5.create_array('/array', old_array)
        # New array with the same node name should delete old array
        h5.root.create_array('/array', new_array, delete_existing=True)
        testing.assert_allclose(h5['/array'], new_array)


def test_delete_existing_dict_with_H5File():
    old_dict = {'a': 'Goose'}
    new_dict = {'b': 'Quail'}
    with open_h5file(H5_TEST_FILE, mode='w', delete_existing=True) as h5:
        h5.create_dict('/dict', old_dict)
        # New dict with the same node name should delete old dict
        h5.create_dict('/dict', new_dict)
        assert h5['/dict'].data == new_dict


def test_delete_existing_dict_with_H5Group():
    old_dict = {'a': 'Goose'}
    new_dict = {'b': 'Quail'}
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5.create_dict('/dict', old_dict)
        # New dict with the same node name should delete old dict
        h5.root.create_dict('/dict', new_dict, delete_existing=True)
        assert h5['/dict'].data == new_dict


def test_delete_existing_table_with_H5File():
    old_description = [('Honk', 'int'), ('Wink', 'float')]
    new_description = [('Toot', 'float'), ('Pop', 'int')]
    with open_h5file(H5_TEST_FILE, mode='w', delete_existing=True) as h5:
        h5.create_table('/table', old_description)
        # New table with the same node name should delete old table
        h5.create_table('/table', new_description)
        tab = h5['/table']
        tab.append({'Pop': (1,), 'Toot': (np.pi,)})
        assert tab.ix[0][0] == np.pi


def test_delete_existing_table_with_H5Group():
    old_description = [('Honk', 'int'), ('Wink', 'float')]
    new_description = [('Toot', 'float'), ('Pop', 'int')]
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5.create_table('/table', old_description)
        # New table with the same node name should delete old table
        h5.root.create_table('/table', new_description, delete_existing=True)
        tab = h5['/table']
        tab.append({'Pop': (1,), 'Toot': (np.pi,)})
        assert tab.ix[0][0] == np.pi


def test_delete_existing_group_with_H5File():
    with open_h5file(H5_TEST_FILE, mode='w', delete_existing=True) as h5:
        h5.create_group('/group')
        grp = h5['/group']
        grp.attrs['test'] = 4

        assert grp.attrs['test'] == 4

        h5.create_group('/group')
        grp = h5['/group']
        grp.attrs['test'] = 6

        assert grp.attrs['test'] == 6


def test_delete_existing_group_with_H5Group():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5.create_group('/group')
        grp = h5['/group']
        grp.attrs['test'] = 4

        assert grp.attrs['test'] == 4

        h5.root.create_group('/group', delete_existing=True)
        grp = h5['/group']
        grp.attrs['test'] = 6

        assert grp.attrs['test'] == 6


def test_remove_group_with_H5File():
    with open_h5file(H5_TEST_FILE, mode='w', delete_existing=True) as h5:
        h5.create_group('/group')
        assert '/group' in h5
        h5.remove_group('/group')
        assert '/group' not in h5


def test_remove_group_with_H5Group():
    node_path = '/waterbear/group'
    with open_h5file(H5_TEST_FILE, mode='w', delete_existing=True) as h5:
        group = h5.create_group('/waterbear')
        group.create_group('group')
        assert node_path in h5
        group.remove_group('group')
        assert node_path not in h5


@testing.raises(ValueError)
def test_remove_group_with_remove_node():
    node_path = '/group'
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5.create_group(node_path)
        h5.remove_node(node_path)  # Groups should be removed w/ `remove_group`


def test_remove_node_with_H5File():
    with open_h5file(H5_TEST_FILE, mode='w', delete_existing=True) as h5:
        h5.create_array('/array', np.arange(3))
        assert '/array' in h5
        h5.remove_node('/array')
        assert '/array' not in h5


def test_remove_node_with_H5Group():
    node_path = '/waterbear/array'
    with open_h5file(H5_TEST_FILE, mode='w', delete_existing=True) as h5:
        group = h5.create_group('/waterbear')
        h5.create_array(node_path, np.arange(3))
        assert node_path in h5
        group.remove_node('array')
        assert node_path not in h5


def test_read_mode_raises_on_nonexistent_file():
    cm = open_h5file('_nonexistent_.h5', mode='r')
    testing.assert_raises(IOError, cm.__enter__)
    cm = open_h5file('_nonexistent_.h5', mode='r+')
    testing.assert_raises(IOError, cm.__enter__)


def test_cleanup():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5_pytables = h5._h5  # This reference gets deleted on close
    assert not h5_pytables.isopen


def test_create_group_with_H5File():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        h5.create_group('/group')
        assert '/group' in h5


def test_create_group_with_H5Group():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        group = h5['/']
        group.create_group('group')
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


def test_group_properties():
    with open_h5file(H5_TEST_FILE, mode='w', auto_groups=True) as h5:
        h5.create_array('/group1/group2/array', np.arange(3))
        h5.create_array('/group1/array1', np.arange(3))

        assert h5['/group1'].name == 'group1'

        child_names = h5['/group1'].children_names
        assert sorted(child_names) == sorted(['group2', 'array1'])

        sub_names = h5['/group1'].subgroup_names
        assert sub_names == ['group2']

        assert h5['/group1'].root.name == '/'
        assert h5['/group1/group2'].root.name == '/'


def test_iter_groups():
    with open_h5file(H5_TEST_FILE, mode='w', auto_groups=True) as h5:
        h5.create_array('/group1/array', np.arange(3))
        h5.create_array('/group1/subgroup/deep_array', np.arange(3))
        group = h5['/group1']
        assert set(n.name for n in group.iter_groups()) == set(['subgroup'])


def test_mapping_interface_for_file():
    with open_h5file(H5_TEST_FILE, mode='w', auto_groups=True) as h5:
        array = h5.create_array('/array', np.arange(3))
        h5.create_array('/group/deep_array', np.arange(3))
        # `deep_array` isn't a direct descendent and isn't counted.
        assert len(h5) == 2
        assert '/group' in h5
        assert '/array' in h5
        testing.assert_allclose(h5['/array'], array)
        assert set(n.name for n in h5) == set(['array', 'group'])


def test_mapping_interface_for_group():
    with open_h5file(H5_TEST_FILE, mode='w', auto_groups=True) as h5:
        array = h5.create_array('/group1/array', np.arange(3))
        h5.create_array('/group1/subgroup/deep_array', np.arange(3))
        group = h5['/group1']
        # `deep_array` isn't a direct descendent and isn't counted.
        assert len(group) == 2
        assert 'subgroup' in group
        assert 'array' in group
        testing.assert_allclose(group['array'], array)
        assert set(n.name for n in group) == set(['array', 'subgroup'])


def test_group_str_and_repr():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        group = h5['/']

        assert str(group) == str(group._h5_group)
        assert repr(group) == repr(group._h5_group)


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


def test_del_attribute():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        attrs = h5['/'].attrs
        attrs['name'] = 'hello'
        del attrs['name']
        assert 'name' not in attrs


def test_get_attribute_default():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        assert h5['/'].attrs.get('missing', 'null') == 'null'


def test_attribute_update():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        attrs = h5['/'].attrs
        attrs.update({'a': 1, 'b': 2})
        assert attrs['a'] == 1
        assert attrs['b'] == 2
        attrs.update({'b': 20, 'c': 30})
        assert attrs['b'] == 20
        assert attrs['c'] == 30


def test_attribute_iteration_methods():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        attrs = h5['/'].attrs
        attrs['organ'] = 'gallbladder'
        attrs['count'] = 42
        attrs['alpha'] = 0xff

        items = list(attrs.items())

        assert all(isinstance(x, tuple) for x in items)

        # unfold the pairs
        keys, vals = [list(item) for item in zip(*items)]

        assert keys == list(attrs.keys())
        assert vals == list(attrs.values())

        # Check that __iter__ is consistent
        assert keys == list(iter(attrs))
        assert len(attrs) == len(keys)


def test_bad_node_name():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        testing.assert_raises(ValueError, h5.create_array,
                              '/attrs', np.zeros(3))


def test_bad_group_name():
    with open_h5file(H5_TEST_FILE, mode='w') as h5:
        testing.assert_raises(ValueError, h5.create_array,
                              '/attrs/array', np.zeros(3))


def test_create_dict_with_H5File():
    data = {'a': 1}
    with temp_h5_file() as h5:
        h5.create_dict('/dict', data)
        assert isinstance(h5['/dict'], H5DictNode)
        assert h5['/dict']['a'] == 1


def test_create_dict_with_H5Group():
    node_path = '/bananas/dict'
    data = {'a': 1}
    with temp_h5_file() as h5:
        group = h5.create_group('/bananas')
        group.create_dict('dict', data)
        assert isinstance(h5[node_path], H5DictNode)
        assert h5[node_path]['a'] == 1


def test_create_table_with_H5File():
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


def test_create_table_with_H5Group():
    node_path = '/rhinocerous/table'
    description = [('foo', 'int'), ('bar', 'float')]
    with temp_h5_file() as h5:
        group = h5.create_group('/rhinocerous')
        group.create_table('table', description)
        tab = h5[node_path]
        assert isinstance(tab, H5TableNode)
        tab.append({'foo': (1,), 'bar': (np.pi,)})
        assert tab.ix[0][0] == 1
        assert tab.ix[0][1] == np.pi

        group.remove_node('table')
        assert node_path not in h5


if __name__ == '__main__':
    testing.run_module_suite()
