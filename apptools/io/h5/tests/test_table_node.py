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
    pandas,
    tables,
    requires_numpy,
    requires_pandas,
    requires_tables,
)

if np is not None and tables is not None:
    from ..table_node import H5TableNode
    from .utils import temp_h5_file


NODE = "/table_node"


@requires_numpy
@requires_tables
class TableNodeTestCase(unittest.TestCase):
    def test_basics(self):
        description = [("a", np.float64), ("b", np.float64)]
        with temp_h5_file() as h5:
            h5table = H5TableNode.add_to_h5file(h5, NODE, description)
            h5table.append({"a": [1, 2], "b": [3, 4]})

            np.testing.assert_allclose(h5table["a"], [1, 2])
            np.testing.assert_allclose(h5table["b"], [3, 4])

        dtype_description = np.dtype([("c", "f4"), ("d", "f4")])
        with temp_h5_file() as h5:
            h5table = H5TableNode.add_to_h5file(h5, NODE, dtype_description)
            h5table.append({"c": [1.2, 3.4], "d": [5.6, 7.8]})

            np.testing.assert_allclose(h5table["c"], [1.2, 3.4])
            np.testing.assert_allclose(h5table["d"], [5.6, 7.8])

            assert len(repr(h5table)) > 0

    def test_getitem(self):
        description = [("a", np.float64), ("b", np.float64)]
        with temp_h5_file() as h5:
            h5table = H5TableNode.add_to_h5file(h5, NODE, description)
            h5table.append({"a": [1, 2], "b": [3, 4]})
            np.testing.assert_allclose(h5table["a"], (1, 2))
            np.testing.assert_allclose(h5table[["b", "a"]], [(3, 1), (4, 2)])

    def test_keys(self):
        description = [("hello", "int"), ("world", "int"), ("Qux1", "bool")]
        with temp_h5_file() as h5:
            keys = set(list(zip(*description))[0])
            h5table = H5TableNode.add_to_h5file(h5, NODE, description)
            assert set(h5table.keys()) == keys

    @requires_pandas
    def test_to_dataframe(self):
        description = [("a", np.float64)]
        with temp_h5_file() as h5:
            h5table = H5TableNode.add_to_h5file(h5, NODE, description)
            h5table.append({"a": [1, 2, 3]})
            df = h5table.to_dataframe()
            assert isinstance(df, pandas.DataFrame)
            np.testing.assert_allclose(df["a"], h5table["a"])


if __name__ == "__main__":
    from numpy import testing

    testing.run_module_suite()
