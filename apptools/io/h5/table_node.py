# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
import numpy as np

from tables.table import Table as PyTablesTable


class _TableRowAccessor(object):
    """A simple object which provides read access to the rows in a Table."""

    def __init__(self, h5_table):
        self._h5_table = h5_table

    def __getitem__(self, key):
        return self._h5_table[key]


class H5TableNode(object):
    """A wrapper for PyTables Table nodes.

    Parameters
    ----------
    node : tables.Table instance
        An H5 node which is a pytables.Table or H5TableNode instance
    """

    def __init__(self, node):
        # Avoid a circular import
        from .file import H5Attrs

        assert self.is_table_node(node)
        self._h5_table = node._h5_table if hasattr(node, "_h5_table") else node
        self.attrs = H5Attrs(self._h5_table._v_attrs)

    # --------------------------------------------------------------------------
    #  Creation methods
    # --------------------------------------------------------------------------

    @classmethod
    def add_to_h5file(cls, h5, node_path, description, **kwargs):
        """Add table node to an H5 file at the specified path.

        Parameters
        ----------
        h5 : H5File
            The H5 file where the table node will be stored.
        node_path : str
            Path to node where data is stored (e.g. '/path/to/my_table')
        description : list of tuples or numpy dtype object
            The description of the columns in the table. This is either a list
            of (column name, dtype, [, shape or itemsize]) tuples or a numpy
            record array dtype. For more information, see the documentation for
            `Table` in PyTables.
        **kwargs : dict
            Additional keyword arguments to pass to pytables.File.create_table
        """
        if isinstance(description, (tuple, list)):
            description = np.dtype(description)

        cls._create_pytables_node(h5, node_path, description, **kwargs)
        node = h5[node_path]

        return cls(node)

    @classmethod
    def is_table_node(cls, pytables_node):
        """Return True if pytables_node is a pytables.Table or a H5TableNode.
        """
        return isinstance(pytables_node, (PyTablesTable, H5TableNode))

    # --------------------------------------------------------------------------
    #  Public interface
    # --------------------------------------------------------------------------

    def append(self, data):
        """Add some data to the table.

        Parameters
        ----------
        data : dict
            A dictionary of column name -> values items
        """
        rows = list(zip(*[data[name] for name in self.keys()]))
        self._h5_table.append(rows)

    def __getitem__(self, col_or_cols):
        """Return one or more columns of data from the table.

        Parameters
        ----------
        col_or_cols : str or list of str
            A single column name or a list of column names

        Return
        ------
        data : ndarray
            An array of column data with the column order matching that of
            `col_or_cols`.
        """
        if isinstance(col_or_cols, str):
            return self._h5_table.col(col_or_cols)

        column_data = [self._h5_table.col(name) for name in col_or_cols]
        return np.column_stack(column_data)

    @property
    def ix(self):
        """Return an object which provides access to row data."""
        return _TableRowAccessor(self._h5_table)

    def keys(self):
        return self._h5_table.colnames

    def to_dataframe(self):
        """Return table data as a pandas `DataFrame`.

        XXX: This does not work if the table contains a multidimensional column

        This method requires pandas to have been installed in the environment.
        """
        from pandas import DataFrame

        # Slicing rows gives a numpy struct array, which DataFrame understands.
        return DataFrame(self.ix[:])

    # --------------------------------------------------------------------------
    #  Object interface
    # --------------------------------------------------------------------------

    def __repr__(self):
        return repr(self._h5_table)

    def __len__(self):
        return self._h5_table.nrows

    # --------------------------------------------------------------------------
    #  Private interface
    # --------------------------------------------------------------------------

    def _f_remove(self):
        """Implement the PyTables `Node._f_remove` method so that H5File
        doesn't choke when trying to remove our node.
        """
        self._h5_table._f_remove()
        self._h5_table = None

    @classmethod
    def _create_pytables_node(cls, h5, node_path, description, **kwargs):
        path, name = h5.split_path(node_path)
        pyt_file = h5._h5
        pyt_file.create_table(path, name, description, **kwargs)
