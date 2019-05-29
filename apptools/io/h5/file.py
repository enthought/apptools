from collections import Mapping, MutableMapping
from functools import partial

import numpy as np
import tables

from .dict_node import H5DictNode
from .table_node import H5TableNode


def get_atom(dtype):
    """ Return a PyTables Atom for the given dtype or dtype string.
    """
    return tables.Atom.from_dtype(np.dtype(dtype))


def iterator_length(iterator):
    return sum(1 for _ in iterator)


def _update_wrapped_docstring(wrapped, original=None):
    PREAMBLE = """\
** H5Group wrapper for H5File.{func_name}: **
Note that the first argument is a nodepath relative to the group, rather than
an absolute path. Below is the original docstring:

    """.format(func_name=wrapped.__name__)
    wrapped.__doc__ = PREAMBLE + original.__doc__
    return wrapped


def h5_group_wrapper(original):
    return partial(_update_wrapped_docstring, original=original)


class H5File(Mapping):
    """File object for HDF5 files.

    This class wraps PyTables to provide a cleaner, but only implements an
    interface for accessing arrays.

    Parameters
    ----------
    filename : str or a `tables.File` instance
        Filename for an HDF5 file, or a PyTables `File` object.
    mode : str
        Mode to open the file:

            'r' : Read-only
            'w' : Write; create new file (an existing file would be deleted).
            'a' : Read and write to file; create if not existing
            'r+': Read and write to file; must already exist

    delete_existing : bool
        If True, an existing node will be deleted when a `create_*` method is
        called. Otherwise, a ValueError will be raise.
    auto_groups : bool
        If True, `create_array` will automatically create parent groups.
    auto_open : bool
        If True, open the file automatically on initialization. Otherwise,
        you can call `H5File.open()` explicitly after initialization.
    chunked : bool
        If True, the default behavior of `create_array` will be a chunked
        array (see PyTables `create_carray`).

    """
    exists_error = ("'{}' exists in '{}'; set `delete_existing` attribute "
                    "to True to overwrite existing calculations.")

    def __init__(self, filename, mode='r+', delete_existing=False,
                 auto_groups=True, auto_open=True, h5filters=None):
        self.mode = mode
        self.delete_existing = delete_existing
        self.auto_groups = auto_groups
        if h5filters is None:
            self.h5filters = tables.Filters(complib='blosc', complevel=5,
                                            shuffle=True)
        self._h5 = None

        if isinstance(filename, tables.File):
            pyt_file = filename
            filename = pyt_file.filename
            if pyt_file.isopen:
                self._h5 = pyt_file

        self.filename = filename
        if auto_open:
            self.open()

    def open(self):
        if not self.is_open:
            self._h5 = tables.open_file(self.filename, mode=self.mode)

    def close(self):
        if self.is_open:
            self._h5.close()
        self._h5 = None

    @property
    def root(self):
        return self['/']

    @property
    def is_open(self):
        return self._h5 is not None

    def __str__(self):
        return str(self._h5)

    def __repr__(self):
        return repr(self._h5)

    def __contains__(self, node_path):
        return node_path in self._h5

    def __getitem__(self, node_path):
        try:
            node = self._h5.get_node(node_path)
        except tables.NoSuchNodeError:
            msg = "Node {0!r} not found in {1!r}"
            raise NameError(msg.format(node_path, self.filename))
        return _wrap_node(node)

    def __iter__(self):
        return (_wrap_node(n) for n in self._h5.iter_nodes(where='/'))

    def __len__(self):
        return iterator_length(self)

    def iteritems(self, path='/'):
        """ Iterate over node paths and nodes of the h5 file. """
        for node in self._h5.walk_nodes(where=path):
            node_path = node._v_pathname
            yield node_path, _wrap_node(node)

    def create_array(self, node_path, array_or_shape, dtype=None,
                     chunked=False, extendable=False, **kwargs):
        """Create node to store an array.

        Parameters
        ----------
        node_path : str
            PyTable node path; e.g. '/path/to/node'.
        array_or_shape : array or shape tuple
            Array or shape tuple for an array. If given a shape tuple, the
            `dtype` parameter must also specified.
        dtype : str or numpy.dtype
            Data type of array. Only necessary if `array_or_shape` is a shape.
        chunked : bool
            Controls whether the array is chunked.
        extendable : {None | bool}
            Controls whether the array is extendable.
        kwargs : key/value pairs
            Keyword args passed to PyTables `File.create_(c|e)array`.
        """
        self._check_node(node_path)
        self._assert_valid_path(node_path)

        h5 = self._h5

        if isinstance(array_or_shape, tuple):
            if dtype is None:
                msg = "`dtype` must be specified if only given array shape."
                raise ValueError(msg)
            array = None
            dtype = dtype
            shape = array_or_shape
        else:
            array = array_or_shape
            dtype = array.dtype.name
            shape = array.shape

        path, name = self.split_path(node_path)
        if extendable:
            shape = (0,) + shape[1:]
            atom = get_atom(dtype)
            node = h5.create_earray(path, name, atom, shape,
                                    filters=self.h5filters, **kwargs)
            if array is not None:
                node.append(array)
        elif chunked:
            atom = get_atom(dtype)
            node = h5.create_carray(path, name, atom, shape,
                                    filters=self.h5filters, **kwargs)
            if array is not None:
                node[:] = array
        else:
            if array is None:
                array = np.zeros(shape, dtype=dtype)
            node = h5.create_array(path, name, array, **kwargs)
        return node

    def create_group(self, group_path, **kwargs):
        """Create group.

        Parameters
        ----------
        group_path : str
            PyTable group path; e.g. '/path/to/group'.
        kwargs : key/value pairs
            Keyword args passed to PyTables `File.create_group`.
        """
        self._check_node(group_path)
        self._assert_valid_path(group_path)
        path, name = self.split_path(group_path)
        self._h5.create_group(path, name, **kwargs)
        return self[group_path]

    def create_dict(self, node_path, data=None, **kwargs):
        """ Create dict node at the specified path.

        Parameters
        ----------
        node_path : str
            Path to node where data is stored (e.g. '/path/to/my_dict')
        data : dict
            Data for initialization, if desired.
        """
        self._check_node(node_path)
        self._assert_valid_path(node_path)
        H5DictNode.add_to_h5file(self, node_path, data=data, **kwargs)
        return self[node_path]

    def create_table(self, node_path, description, **kwargs):
        """ Create table node at the specified path.

        Parameters
        ----------
        node_path : str
            Path to node where data is stored (e.g. '/path/to/my_dict')
        description : dict or numpy dtype object
            The description of the columns in the table. This is either a dict
            of column name -> dtype items or a numpy record array dtype. For
            more information, see the documentation for Table in pytables.
        """
        self._check_node(node_path)
        self._assert_valid_path(node_path)
        H5TableNode.add_to_h5file(self, node_path, description, **kwargs)
        return self[node_path]

    def _check_node(self, node_path):
        """Check if node exists and create parent groups if necessary.

        Either raise error or delete depending on `delete_existing` attribute.
        """
        if self.auto_groups:
            path, name = self.split_path(node_path)
            self._create_required_groups(path)

        if node_path in self:
            if self.delete_existing:
                if isinstance(self[node_path], H5Group):
                    self.remove_group(node_path, recursive=True)
                else:
                    self.remove_node(node_path)
            else:
                msg = self.exists_error.format(node_path, self.filename)
                raise ValueError(msg)

    def _create_required_groups(self, path):
        if path not in self:
            parent, missing = self.split_path(path)
            # Call recursively to ensure that all parent groups exist.
            self._create_required_groups(parent)
            self.create_group(path)

    def remove_node(self, node_path):
        """Remove node

        Parameters
        ----------
        node_path : str
            PyTable node path; e.g. '/path/to/node'.
        """
        node = self[node_path]
        if isinstance(node, H5Group):
            msg = "{!r} is a group. Use `remove_group` to remove group nodes."
            raise ValueError(msg.format(node.pathname))
        node._f_remove()

    def remove_group(self, group_path, **kwargs):
        """Remove group

        Parameters
        ----------
        group_path : str
            PyTable group path; e.g. '/path/to/group'.
        """
        self[group_path]._h5_group._g_remove(**kwargs)

    @classmethod
    def _assert_valid_path(self, node_path):
        if 'attrs' in node_path.split('/'):
            raise ValueError("'attrs' is an invalid node name.")

    @classmethod
    def split_path(cls, node_path):
        """Split node path returning the base path and node name.

        For example: '/path/to/node' will return '/path/to' and 'node'

        Parameters
        ----------
        node_path : str
            PyTable node path; e.g. '/path/to/node'.
        """
        i = node_path.rfind('/')
        if i == 0:
            return '/', node_path[1:]
        else:
            return node_path[:i], node_path[i + 1:]

    @classmethod
    def join_path(cls, *args):
        """Join parts of an h5 path.

        For example, the 3 argmuments 'path', 'to', 'node' will return
        '/path/to/node'.

        Parameters
        ----------
        args : str
            Parts of path to be joined.
        """
        path = '/'.join(part.strip('/') for part in args)
        if not path.startswith('/'):
            path = '/' + path
        return path


class H5Attrs(MutableMapping):
    """ An attributes dictionary for an h5 node.

    This intercepts `__setitem__` so that python sequences can be converted to
    numpy arrays. This helps preserve the readability of our HDF5 files by
    other (non-python) programs.
    """

    def __init__(self, node_attrs):
        self._node_attrs = node_attrs

    def __delitem__(self, key):
        del self._node_attrs[key]

    def __getitem__(self, key):
        return self._node_attrs[key]

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self._node_attrs._f_list())

    def __setitem__(self, key, value):
        if isinstance(value, tuple) or isinstance(value, list):
            value = np.array(value)
        self._node_attrs[key] = value

    def get(self, key, default=None):
        return default if key not in self else self[key]

    def keys(self):
        return self._node_attrs._f_list()

    def values(self):
        return [self[k] for k in self.keys()]

    def items(self):
        return [(k, self[k]) for k in self.keys()]


class H5Group(Mapping):
    """ A group node in an H5File.

    This is a thin wrapper around PyTables' Group object to expose attributes
    and maintain the dict interface of H5File.
    """

    def __init__(self, pytables_group):
        self._h5_group = pytables_group
        self.attrs = H5Attrs(self._h5_group._v_attrs)

    def __contains__(self, node_path):
        return node_path in self._h5_group

    def __str__(self):
        return str(self._h5_group)

    def __repr__(self):
        return repr(self._h5_group)

    def __getitem__(self, node_path):
        parts = node_path.split('/')
        # PyTables stores children as attributes
        node = self._h5_group.__getattr__(parts[0])
        node = _wrap_node(node)
        if len(parts) == 1:
            return node
        else:
            return node['/'.join(parts[1:])]

    def __iter__(self):
        return (_wrap_node(c) for c in self._h5_group)

    def __len__(self):
        return iterator_length(self)

    @property
    def pathname(self):
        return self._h5_group._v_pathname

    @property
    def name(self):
        return self._h5_group._v_name

    @property
    def filename(self):
        return self._h5_group._v_file.filename

    @property
    def root(self):
        return _wrap_node(self._h5_group._v_file.root)

    @property
    def children_names(self):
        return list(self._h5_group._v_children.keys())

    @property
    def subgroup_names(self):
        return list(self._h5_group._v_groups.keys())

    def iter_groups(self):
        """ Iterate over `H5Group` nodes that are children of this group. """
        return (_wrap_node(g) for g in self._h5_group._v_groups.itervalues())

    @h5_group_wrapper(H5File.create_group)
    def create_group(self, group_subpath, delete_existing=False, **kwargs):
        return self._delegate_to_h5file('create_group', group_subpath,
                                        delete_existing=delete_existing,
                                        **kwargs)

    @h5_group_wrapper(H5File.remove_group)
    def remove_group(self, group_subpath, **kwargs):
        return self._delegate_to_h5file('remove_group', group_subpath,
                                        **kwargs)

    @h5_group_wrapper(H5File.create_array)
    def create_array(self, node_subpath, array_or_shape, dtype=None,
                     chunked=False, extendable=False, **kwargs):
        return self._delegate_to_h5file('create_array', node_subpath,
                                        array_or_shape, dtype=dtype,
                                        chunked=chunked, extendable=extendable,
                                        **kwargs)

    @h5_group_wrapper(H5File.create_table)
    def create_table(self, node_subpath, description, *args, **kwargs):
        return self._delegate_to_h5file('create_table', node_subpath,
                                        description, *args, **kwargs)

    @h5_group_wrapper(H5File.create_dict)
    def create_dict(self, node_subpath, data=None, **kwargs):
        return self._delegate_to_h5file('create_dict', node_subpath, data=data,
                                        **kwargs)

    @h5_group_wrapper(H5File.remove_node)
    def remove_node(self, node_subpath, **kwargs):
        return self._delegate_to_h5file('remove_node', node_subpath, **kwargs)

    def _delegate_to_h5file(self, function_name, node_subpath,
                            *args, **kwargs):
        delete_existing = kwargs.pop('delete_existing', False)
        h5 = H5File(self._h5_group._v_file, delete_existing=delete_existing)
        group_path = h5.join_path(self.pathname, node_subpath)
        func = getattr(h5, function_name)
        return func(group_path, *args, **kwargs)


def _wrap_node(node):
    """ Wrap PyTables node object, if necessary. """
    if isinstance(node, tables.Group):
        if H5DictNode.is_dict_node(node):
            node = H5DictNode(node)
        else:
            node = H5Group(node)
    elif H5TableNode.is_table_node(node):
        node = H5TableNode(node)
    return node
