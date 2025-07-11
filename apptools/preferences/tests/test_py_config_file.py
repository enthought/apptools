# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Tests for Python-esque '.ini' files. """


# Standard library imports.
import os
import tempfile
import unittest
from os.path import join

# Major package imports.
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

# Enthought library imports.
from .py_config_file import PyConfigFile


# This module's package.
PKG = "apptools.preferences.tests"


class PyConfigFileTestCase(unittest.TestCase):
    """ Tests for Python-esque '.ini' files. """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        # The filenames of the example preferences files.
        self.example = os.fspath(files(PKG) / "py_config_example.ini")
        self.example_2 = os.fspath(files(PKG) / "py_config_example_2.ini")

    def tearDown(self):
        """ Called immediately after each test method has been called. """

    ###########################################################################
    # Tests.
    ###########################################################################

    def test_load_from_filename(self):
        """ load from filename """

        config = PyConfigFile(self.example)

        self.assertEqual("blue", config["acme.ui"]["bgcolor"])
        self.assertEqual(50, config["acme.ui"]["width"])
        self.assertEqual(1.0, config["acme.ui"]["ratio"])
        self.assertEqual(True, config["acme.ui"]["visible"])
        self.assertEqual({"a": 1, "b": 2}, config["acme.ui"]["foo"])
        self.assertEqual([1, 2, 3, 4], config["acme.ui"]["bar"])
        self.assertEqual((1, "a", 6, 4), config["acme.ui"]["baz"])
        self.assertEqual("red", config["acme.ui.other"]["fred"])
        self.assertEqual(100, config["acme.ui.other"]["wilma"])
        self.assertEqual(90, config["tds.foogle"]["joe"])
        self.assertEqual("meerkat", config["simples"]["animal"])

    def test_load_from_file(self):
        """ load from file """

        config = PyConfigFile(open(self.example))

        self.assertEqual("blue", config["acme.ui"]["bgcolor"])
        self.assertEqual(50, config["acme.ui"]["width"])
        self.assertEqual(1.0, config["acme.ui"]["ratio"])
        self.assertEqual(True, config["acme.ui"]["visible"])
        self.assertEqual({"a": 1, "b": 2}, config["acme.ui"]["foo"])
        self.assertEqual([1, 2, 3, 4], config["acme.ui"]["bar"])
        self.assertEqual((1, "a", 6, 4), config["acme.ui"]["baz"])
        self.assertEqual("red", config["acme.ui.other"]["fred"])
        self.assertEqual(100, config["acme.ui.other"]["wilma"])
        self.assertEqual(90, config["tds.foogle"]["joe"])
        self.assertEqual("meerkat", config["simples"]["animal"])

    def test_save(self):
        """ save """

        config = PyConfigFile(open(self.example))

        self.assertEqual("blue", config["acme.ui"]["bgcolor"])
        self.assertEqual(50, config["acme.ui"]["width"])
        self.assertEqual(1.0, config["acme.ui"]["ratio"])
        self.assertEqual(True, config["acme.ui"]["visible"])
        self.assertEqual({"a": 1, "b": 2}, config["acme.ui"]["foo"])
        self.assertEqual([1, 2, 3, 4], config["acme.ui"]["bar"])
        self.assertEqual("red", config["acme.ui.other"]["fred"])
        self.assertEqual(100, config["acme.ui.other"]["wilma"])
        self.assertEqual(90, config["tds.foogle"]["joe"])
        self.assertEqual("meerkat", config["simples"]["animal"])

        # Save the config to another file.
        tmpdir = tempfile.mkdtemp()
        tmp = join(tmpdir, "tmp.ini")

        config.save(tmp)
        try:
            self.assertTrue(os.path.exists(tmp))

            # Make sure we can read the file back in and that we get the same
            # values!
            config = PyConfigFile(open(tmp))

            self.assertEqual("blue", config["acme.ui"]["bgcolor"])
            self.assertEqual(50, config["acme.ui"]["width"])
            self.assertEqual(1.0, config["acme.ui"]["ratio"])
            self.assertEqual(True, config["acme.ui"]["visible"])
            self.assertEqual({"a": 1, "b": 2}, config["acme.ui"]["foo"])
            self.assertEqual([1, 2, 3, 4], config["acme.ui"]["bar"])
            self.assertEqual((1, "a", 6, 4), config["acme.ui"]["baz"])
            self.assertEqual("red", config["acme.ui.other"]["fred"])
            self.assertEqual(100, config["acme.ui.other"]["wilma"])
            self.assertEqual(90, config["tds.foogle"]["joe"])
            self.assertEqual("meerkat", config["simples"]["animal"])

        finally:
            # Clean up!
            os.remove(tmp)
            os.rmdir(tmpdir)

    def test_load_multiple_files(self):
        """ load multiple files """

        config = PyConfigFile(self.example)

        self.assertEqual("blue", config["acme.ui"]["bgcolor"])
        self.assertEqual(50, config["acme.ui"]["width"])
        self.assertEqual(1.0, config["acme.ui"]["ratio"])
        self.assertEqual(True, config["acme.ui"]["visible"])
        self.assertEqual({"a": 1, "b": 2}, config["acme.ui"]["foo"])
        self.assertEqual([1, 2, 3, 4], config["acme.ui"]["bar"])
        self.assertEqual((1, "a", 6, 4), config["acme.ui"]["baz"])
        self.assertEqual("red", config["acme.ui.other"]["fred"])
        self.assertEqual(100, config["acme.ui.other"]["wilma"])
        self.assertEqual(90, config["tds.foogle"]["joe"])
        self.assertEqual("meerkat", config["simples"]["animal"])

        # Load another file.
        config.load(self.example_2)

        # Make sure we still have the unchanged values...
        self.assertEqual("red", config["acme.ui"]["bgcolor"])
        self.assertEqual(50, config["acme.ui"]["width"])
        self.assertEqual(1.0, config["acme.ui"]["ratio"])
        self.assertEqual(True, config["acme.ui"]["visible"])
        self.assertEqual({"a": 1, "b": 2}, config["acme.ui"]["foo"])
        self.assertEqual([1, 2, 3, 4], config["acme.ui"]["bar"])
        self.assertEqual((1, "a", 6, 4), config["acme.ui"]["baz"])
        self.assertEqual("red", config["acme.ui.other"]["fred"])
        self.assertEqual(100, config["acme.ui.other"]["wilma"])
        self.assertEqual(90, config["tds.foogle"]["joe"])
        self.assertEqual("meerkat", config["simples"]["animal"])

        # ... and the values that were overwritten...
        self.assertEqual("red", config["acme.ui"]["bgcolor"])

        # ... and that we have the new ones.
        self.assertEqual(42, config["acme.ui"]["bazzle"])

        # ... and that the new ones can refer to the old ones!
        self.assertEqual(180, config["acme.ui"]["blimey"])
