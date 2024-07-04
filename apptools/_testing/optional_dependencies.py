# (C) Copyright 2006-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Utilities for handling optional dependencies so that tests for
optional features can be skipped gracefully.
"""
import importlib
import unittest


def optional_import(name):
    """
    Optionally import a module, returning None if that module is unavailable.

    Parameters
    ----------
    name : Str
        The name of the module being imported.

    Returns
    -------
    None or module
        None if the module is not available, and the module otherwise.

    """
    try:
        module = importlib.import_module(name)
    except ImportError:
        return None
    else:
        return module


numpy = optional_import("numpy")
requires_numpy = unittest.skipIf(numpy is None, "NumPy not available")

pandas = optional_import("pandas")
requires_pandas = unittest.skipIf(pandas is None, "Pandas not available")

tables = optional_import("tables")
requires_tables = unittest.skipIf(tables is None, "PyTables not available")

configobj = optional_import("configobj")
requires_configobj = unittest.skipIf(
    configobj is None, "configobj not available"
)

pyface = optional_import("pyface")
requires_pyface = unittest.skipIf(pyface is None, "Pyface not available")

traitsui = optional_import("traitsui")
requires_traitsui = unittest.skipIf(traitsui is None, "TraitsUI not available")
