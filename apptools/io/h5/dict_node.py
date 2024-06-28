# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
from contextlib import closing
import json

from numpy import ndarray

from tables import Group as PyTablesGroup
from tables.nodes import filenode


#: The key name which identifies array objects in the JSON dict.
ARRAY_PROXY_KEY = "__array__"
NODE_KEY = "node_name"


class H5DictNode(object):
    """Dictionary-like node interface.

    Data for the dict is stored as a JSON file in a PyTables FileNode. This
    allows easy storage of Python objects, such as dictionaries and lists of
    different data types.

    Note that this is implemented using a group-node assuming that arrays are
    valid inputs and will be stored as H5 array nodes.

    Parameters
    ----------
    h5_group : H5Group instance
        Group node which will be used as a dictionary store.
    auto_flush : bool
        If True, write data to disk whenever the dict data is altered.
        Otherwise, call `flush()` explicitly to write data to disk.
    """

    #: Name of filenode where dict data is stored.
    _pyobject_data_node = "_pyobject_data"

    def __init__(self, h5_group, auto_flush=True):
        assert self.is_dict_node(h5_group)

        h5_group = self._get_pyt_group(h5_group)
        self._h5_group = h5_group
        self.auto_flush = auto_flush

        # Load dict data from the file node.
        dict_node = getattr(h5_group, self._pyobject_data_node)
        with closing(filenode.open_node(dict_node)) as f:
            self._pyobject_data = json.loads(
                f.read().decode("ascii"), object_hook=self._object_hook
            )

    # --------------------------------------------------------------------------
    #  Dictionary interface
    # --------------------------------------------------------------------------

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        if self.auto_flush:
            self.flush()

    def __delitem__(self, key):
        del self.data[key]
        if self.auto_flush:
            self.flush()

    def __contains__(self, key):
        return key in self.data

    def keys(self):
        return self.data.keys()

    # --------------------------------------------------------------------------
    #  Public interface
    # --------------------------------------------------------------------------

    @property
    def data(self):
        return self._pyobject_data

    @data.setter
    def data(self, new_data_dict):
        self._pyobject_data = new_data_dict
        if self.auto_flush:
            self.flush()

    def flush(self):
        """ Write buffered data to disk. """
        self._remove_pyobject_node()
        self._write_pyobject_node()

    @classmethod
    def add_to_h5file(cls, h5, node_path, data=None, **kwargs):
        """Add dict node to an H5 file at the specified path.

        Parameters
        ----------
        h5 : H5File
            The H5 file where the dictionary data will be stored.
        node_path : str
            Path to node where data is stored (e.g. '/path/to/my_dict')
        data : dict
            Data for initialization, if desired.
        """
        h5.create_group(node_path)
        group = h5[node_path]

        cls._create_pyobject_node(h5._h5, node_path, data=data)
        return cls(group, **kwargs)

    @classmethod
    def is_dict_node(cls, pytables_node):
        """Return True if PyTables node looks like an H5DictNode.

        NOTE: That this returns False if the node is an `H5DictNode` instance,
        since the input node should be a normal PyTables Group node.
        """
        # Import here to prevent circular imports
        from .file import H5Group

        if isinstance(pytables_node, H5Group):
            pytables_node = cls._get_pyt_group(pytables_node)

        if not isinstance(pytables_node, PyTablesGroup):
            return False

        return cls._pyobject_data_node in pytables_node._v_children

    # --------------------------------------------------------------------------
    #  Private interface
    # --------------------------------------------------------------------------

    def _f_remove(self):
        """This is called by H5File whenever a node is removed.

        All nodes in `_h5_group` will be removed.
        """
        for name in self._h5_group._v_children.keys():
            if name != self._pyobject_data_node:
                self._h5_group.__getattr__(name)._f_remove()
        # Remove the dict node
        self._remove_pyobject_node()
        # Remove the group node
        self._h5_group._f_remove()

    def _object_hook(self, dct):
        """This gets passed object dictionaries by `json.load(s)` and if it
        finds `ARRAY_PROXY_KEY` in the object description it returns the
        proxied array object.
        """
        if ARRAY_PROXY_KEY in dct:
            node_name = dct[NODE_KEY]
            return getattr(self._h5_group, node_name)[:]
        return dct

    def _remove_pyobject_node(self):
        node = getattr(self._h5_group, self._pyobject_data_node)
        node._f_remove()

    def _write_pyobject_node(self):
        pyt_file = self._h5_group._v_file
        node_path = self._h5_group._v_pathname
        self._create_pyobject_node(pyt_file, node_path, self.data)

    @classmethod
    def _create_pyobject_node(cls, pyt_file, node_path, data=None):
        if data is None:
            data = {}

        # Stash the array values in their own h5 nodes and return a dictionary
        # which is appropriate for JSON serialization.
        out_data = cls._handle_array_values(pyt_file, node_path, data)

        kwargs = dict(where=node_path, name=cls._pyobject_data_node)
        with closing(filenode.new_node(pyt_file, **kwargs)) as f:
            f.write(json.dumps(out_data).encode("ascii"))

    @classmethod
    def _get_pyt_group(self, group):
        if hasattr(group, "_h5_group"):
            group = group._h5_group
        return group

    @classmethod
    def _array_proxy(cls, pyt_file, group, key, array):
        """Stores an array as a normal H5 node and returns the proxy object
        which will be serialized to JSON.

        `ARRAY_PROXY_KEY` marks the object dictionary as an array proxy so that
        `_object_hook` can recognize it. `NODE_KEY` stores the node name of the
        array so that `_object_hook` can load the array data when the dict node
        is deserialized.

        """
        if key in group:
            pyt_file.remove_node(group, key)
        pyt_file.create_array(group, key, array)
        return {ARRAY_PROXY_KEY: True, NODE_KEY: key}

    @classmethod
    def _handle_array_values(cls, pyt_file, group_path, data):
        group = pyt_file.get_node(group_path)

        # Convert numpy array values to H5 array nodes.
        out_data = {}
        for key in data.keys():
            value = data[key]
            if isinstance(value, ndarray):
                out_data[key] = cls._array_proxy(pyt_file, group, key, value)
            else:
                out_data[key] = value

        # Remove stored arrays which are no longer in the data dictionary.
        pyt_children = group._v_children
        nodes_to_remove = []
        for key in pyt_children.keys():
            if key not in data:
                nodes_to_remove.append(key)

        for key in nodes_to_remove:
            pyt_file.remove_node(group, key)

        return out_data
