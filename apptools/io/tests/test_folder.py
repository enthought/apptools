# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Tests folder operations. """


# Standard library imports.
import os
import shutil
import stat
import unittest
from os.path import join

# Enthought library imports.
from apptools.io import File


class FolderTestCase(unittest.TestCase):
    """ Tests folder operations on a local file system. """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        shutil.rmtree("data", ignore_errors=True)

        os.mkdir("data")

    def tearDown(self):
        """ Called immediately after each test method has been called. """

        shutil.rmtree("data")

    ###########################################################################
    # Tests.
    ###########################################################################

    def test_properties(self):
        """ folder properties """

        # Properties of a non-existent folder.
        f = File("data/bogus")

        self.assertIn(os.path.abspath(os.path.curdir), f.absolute_path)
        self.assertIsNone(f.children)
        self.assertEqual(f.ext, "")
        self.assertFalse(f.exists)
        self.assertFalse(f.is_file)
        self.assertFalse(f.is_folder)
        self.assertFalse(f.is_package)
        self.assertFalse(f.is_readonly)
        self.assertEqual(f.mime_type, "content/unknown")
        self.assertEqual(f.name, "bogus")
        self.assertEqual(f.parent.path, "data")
        self.assertEqual(f.path, "data/bogus")
        self.assertIn(os.path.abspath(os.path.curdir), f.url)
        self.assertEqual(str(f), "File(%s)" % f.path)

        # Properties of an existing folder.
        f = File("data/sub")
        f.create_folder()

        self.assertIn(os.path.abspath(os.path.curdir), f.absolute_path)
        self.assertEqual(len(f.children), 0)
        self.assertEqual(f.ext, "")
        self.assertTrue(f.exists)
        self.assertFalse(f.is_file)
        self.assertTrue(f.is_folder)
        self.assertFalse(f.is_package)
        self.assertFalse(f.is_readonly)
        self.assertEqual(f.mime_type, "content/unknown")
        self.assertEqual(f.name, "sub")
        self.assertEqual(f.parent.path, "data")
        self.assertEqual(f.path, "data/sub")
        self.assertIn(os.path.abspath(os.path.curdir), f.url)

        # Make it readonly.
        os.chmod(f.path, stat.S_IRUSR)
        self.assertTrue(f.is_readonly)

        # And then make it NOT readonly so that we can delete it at the end of
        # the test!
        os.chmod(f.path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        self.assertFalse(f.is_readonly)

        # Properties of a Python package folder.
        f = File("data/package")
        f.create_folder()

        init = File("data/package/__init__.py")
        init.create_file()

        self.assertIn(os.path.abspath(os.path.curdir), f.absolute_path)
        self.assertEqual(len(f.children), 1)
        self.assertEqual(f.ext, "")
        self.assertTrue(f.exists)
        self.assertFalse(f.is_file)
        self.assertTrue(f.is_folder)
        self.assertTrue(f.is_package)
        self.assertFalse(f.is_readonly)
        self.assertEqual(f.mime_type, "content/unknown")
        self.assertEqual(f.name, "package")
        self.assertEqual(f.parent.path, "data")
        self.assertEqual(f.path, "data/package")
        self.assertIn(os.path.abspath(os.path.curdir), f.url)

    def test_copy(self):
        """ folder copy """

        f = File("data/sub")
        self.assertFalse(f.exists)

        # Create the folder.
        f.create_folder()
        self.assertTrue(f.exists)
        self.assertRaises(ValueError, f.create_folder)

        self.assertEqual(len(f.children), 0)
        self.assertEqual(f.ext, "")
        self.assertFalse(f.is_file)
        self.assertTrue(f.is_folder)
        self.assertEqual(f.mime_type, "content/unknown")
        self.assertEqual(f.name, "sub")
        self.assertEqual(f.path, "data/sub")

        # Copy the folder.
        g = File("data/copy")
        self.assertFalse(g.exists)

        f.copy(g)
        self.assertTrue(g.exists)

        self.assertEqual(len(g.children), 0)
        self.assertEqual(g.ext, "")
        self.assertFalse(g.is_file)
        self.assertTrue(g.is_folder)
        self.assertEqual(g.mime_type, "content/unknown")
        self.assertEqual(g.name, "copy")
        self.assertEqual(g.path, "data/copy")

        # Attempt to copy a non-existent folder (should do nothing).
        f = File("data/bogus")
        self.assertFalse(f.exists)

        g = File("data/bogus_copy")
        self.assertFalse(g.exists)

        f.copy(g)
        self.assertFalse(g.exists)

    def test_create_folder(self):
        """ folder creation """

        f = File("data/sub")
        self.assertFalse(f.exists)

        # Create the folder.
        f.create_folder()
        self.assertTrue(f.exists)

        parent = File("data")
        self.assertEqual(len(parent.children), 1)
        self.assertEqual(parent.children[0].path, join("data", "sub"))

        # Try to create it again.
        self.assertRaises(ValueError, f.create_folder)

    def test_create_folders(self):
        """ nested folder creation """

        f = File("data/sub/foo")
        self.assertFalse(f.exists)

        # Attempt to create the folder with 'create_folder' which requires
        # that all intermediate folders exist.
        self.assertRaises(OSError, f.create_folder)

        # Create the folder.
        f.create_folders()
        self.assertTrue(f.exists)
        self.assertTrue(File("data/sub").exists)

        # Try to create it again.
        self.assertRaises(ValueError, f.create_folders)

    def test_delete(self):
        """ folder deletion """

        f = File("data/sub")
        self.assertFalse(f.exists)

        # Create the folder.
        f.create_folder()
        self.assertTrue(f.exists)
        self.assertRaises(ValueError, f.create_folder)

        self.assertEqual(len(f.children), 0)
        self.assertEqual(f.ext, "")
        self.assertFalse(f.is_file)
        self.assertTrue(f.is_folder)
        self.assertEqual(f.mime_type, "content/unknown")
        self.assertEqual(f.name, "sub")
        self.assertEqual(f.path, "data/sub")

        # Delete it.
        f.delete()
        self.assertFalse(f.exists)

        # Attempt to delete a non-existet folder (should do nothing).
        f = File("data/bogus")
        self.assertFalse(f.exists)

        f.delete()
        self.assertFalse(f.exists)
