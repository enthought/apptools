# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
"""Tests for the file_path module.

"""

# Standard library imports.
import unittest
import os
import sys
from os.path import abspath, dirname, basename, join
from io import BytesIO

# 3rd party imports.
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

from apptools._testing.optional_dependencies import (
    numpy as np,
    requires_numpy,
)

# Enthought library imports.
if np is not None:
    from apptools.persistence import state_pickler
    from apptools.persistence import file_path


@requires_numpy
class Test:
    def __init__(self):
        self.f = file_path.FilePath()


@requires_numpy
class TestFilePath(unittest.TestCase):
    def setUp(self):
        # If the cwd is somewhere under /tmp, that confuses the tests below.
        # Use the directory containing this file, instead.
        test_cwd = os.fspath(files("apptools.persistence") / "")
        self.old_cwd = os.getcwd()
        os.chdir(test_cwd)

    def tearDown(self):
        os.chdir(self.old_cwd)

    def test_relative(self):
        """Test if relative paths are set correctly."""
        fname = "t.vtk"
        f = file_path.FilePath(fname)
        cwd = os.getcwd()
        # Trivial case of both in same dir.
        f.set_relative(abspath(join(cwd, "t.mv2")))
        self.assertEqual(f.rel_pth, fname)
        # Move one directory deeper.
        f.set_relative(abspath(join(cwd, "tests", "t.mv2")))
        self.assertEqual(f.rel_pth, join(os.pardir, fname))
        # Move one directory shallower.
        f.set_relative(abspath(join(dirname(cwd), "t.mv2")))
        diff = basename(cwd)
        self.assertEqual(f.rel_pth, join(diff, fname))
        # Test where the path is relative to the root.
        f.set(abspath(join("data", fname)))
        f.set_relative("/tmp/test.mv2")
        if sys.platform.startswith("win"):
            expect = os.pardir + abspath(join("data", fname))[2:]
        else:
            expect = os.pardir + abspath(join("data", fname))
        self.assertEqual(f.rel_pth, expect)

    def test_absolute(self):
        """Test if absolute paths are set corectly."""
        fname = "t.vtk"
        f = file_path.FilePath(fname)
        cwd = os.getcwd()
        # Easy case of both in same dir.
        f.set_absolute(join(cwd, "foo", "test", "t.mv2"))
        self.assertEqual(f.abs_pth, join(cwd, "foo", "test", fname))
        # One level lower.
        fname = join(os.pardir, "t.vtk")
        f.set(fname)
        f.set_absolute(join(cwd, "foo", "test", "t.mv2"))
        self.assertEqual(f.abs_pth, abspath(join(cwd, "foo", "test", fname)))
        # One level higher.
        fname = join("test", "t.vtk")
        f.set(fname)
        f.set_absolute(join(cwd, "foo", "t.mv2"))
        self.assertEqual(f.abs_pth, abspath(join(cwd, "foo", fname)))

    def test_pickle(self):
        """Test if pickler works correctly with FilePaths."""
        t = Test()
        t.f.set("t.vtk")
        cwd = os.getcwd()
        curdir = basename(cwd)

        # Create a dummy file in the parent dir.
        s = BytesIO()
        # Spoof its location.
        s.name = abspath(join(cwd, os.pardir, "t.mv2"))
        # Dump into it
        state_pickler.dump(t, s)

        # Rewind the stream
        s.seek(0)
        # "Move" the file elsewhere
        s.name = join(cwd, "foo", "test", "t.mv2")
        state = state_pickler.load_state(s)
        self.assertEqual(
            state.f.abs_pth, join(cwd, "foo", "test", curdir, "t.vtk")
        )

        # Create a dummy file in a subdir.
        s = BytesIO()
        # Spoof its location.
        s.name = abspath(join(cwd, "data", "t.mv2"))
        # Dump into it.
        state_pickler.dump(t, s)

        # Rewind the stream
        s.seek(0)
        # "Move" the file elsewhere
        s.name = join(cwd, "foo", "test", "t.mv2")
        state = state_pickler.load_state(s)
        self.assertEqual(state.f.abs_pth, join(cwd, "foo", "t.vtk"))
