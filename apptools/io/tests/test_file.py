# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Tests file operations. """


# Standard library imports.
import os
import shutil
import stat
import unittest

# Enthought library imports.
from apptools.io import File


class FileTestCase(unittest.TestCase):
    """ Tests file operations on a local file system. """

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
        """ file properties """

        # Properties of a non-existent file.
        f = File("data/bogus.xx")

        self.assertIn(os.path.abspath(os.path.curdir), f.absolute_path)
        self.assertIsNone(f.children)
        self.assertEqual(f.ext, ".xx")
        self.assertFalse(f.exists)
        self.assertFalse(f.is_file)
        self.assertFalse(f.is_folder)
        self.assertFalse(f.is_package)
        self.assertFalse(f.is_readonly)
        self.assertEqual(f.mime_type, "content/unknown")
        self.assertEqual(f.name, "bogus")
        self.assertEqual(f.parent.path, "data")
        self.assertEqual(f.path, "data/bogus.xx")
        self.assertIn(os.path.abspath(os.path.curdir), f.url)
        self.assertEqual(str(f), "File(%s)" % f.path)

        # Properties of an existing file.
        f = File("data/foo.txt")
        f.create_file()

        self.assertIn(os.path.abspath(os.path.curdir), f.absolute_path)
        self.assertIsNone(f.children)
        self.assertEqual(f.ext, ".txt")
        self.assertTrue(f.exists)
        self.assertTrue(f.is_file)
        self.assertFalse(f.is_folder)
        self.assertFalse(f.is_package)
        self.assertFalse(f.is_readonly)
        self.assertEqual(f.mime_type, "text/plain")
        self.assertEqual(f.name, "foo")
        self.assertEqual(f.parent.path, "data")
        self.assertEqual(f.path, "data/foo.txt")
        self.assertIn(os.path.abspath(os.path.curdir), f.url)

        # Make it readonly.
        os.chmod(f.path, stat.S_IRUSR)
        self.assertTrue(f.is_readonly)

        # And then make it NOT readonly so that we can delete it at the end of
        # the test!
        os.chmod(f.path, stat.S_IRUSR | stat.S_IWUSR)
        self.assertFalse(f.is_readonly)

    def test_copy(self):
        """ file copy """

        content = 'print("Hello World!")\n'

        f = File("data/foo.txt")
        self.assertFalse(f.exists)

        # Create the file.
        f.create_file(content)
        self.assertTrue(f.exists)
        self.assertRaises(ValueError, f.create_file, content)

        self.assertIsNone(f.children)
        self.assertEqual(f.ext, ".txt")
        self.assertTrue(f.is_file)
        self.assertFalse(f.is_folder)
        self.assertEqual(f.mime_type, "text/plain")
        self.assertEqual(f.name, "foo")
        self.assertEqual(f.path, "data/foo.txt")

        # Copy the file.
        g = File("data/bar.txt")
        self.assertFalse(g.exists)

        f.copy(g)
        self.assertTrue(g.exists)

        self.assertIsNone(g.children)
        self.assertEqual(g.ext, ".txt")
        self.assertTrue(g.is_file)
        self.assertFalse(g.is_folder)
        self.assertEqual(g.mime_type, "text/plain")
        self.assertEqual(g.name, "bar")
        self.assertEqual(g.path, "data/bar.txt")

        # Attempt to copy a non-existent file (should do nothing).
        f = File("data/bogus.xx")
        self.assertFalse(f.exists)

        g = File("data/bogus_copy.txt")
        self.assertFalse(g.exists)

        f.copy(g)
        self.assertFalse(g.exists)

    def test_create_file(self):
        """ file creation """

        content = 'print("Hello World!")\n'

        f = File("data/foo.txt")
        self.assertFalse(f.exists)

        # Create the file.
        f.create_file(content)
        self.assertTrue(f.exists)
        with open(f.path) as file:
            self.assertEqual(file.read(), content)

        # Try to create it again.
        self.assertRaises(ValueError, f.create_file, content)

    def test_delete(self):
        """ file deletion """

        content = 'print("Hello World!")\n'

        f = File("data/foo.txt")
        self.assertFalse(f.exists)

        # Create the file.
        f.create_file(content)
        self.assertTrue(f.exists)
        self.assertRaises(ValueError, f.create_file, content)

        self.assertIsNone(f.children)
        self.assertEqual(f.ext, ".txt")
        self.assertTrue(f.is_file)
        self.assertFalse(f.is_folder)
        self.assertEqual(f.mime_type, "text/plain")
        self.assertEqual(f.name, "foo")
        self.assertEqual(f.path, "data/foo.txt")

        # Delete it.
        f.delete()
        self.assertFalse(f.exists)

        # Attempt to delete a non-existet file (should do nothing).
        f = File("data/bogus.txt")
        self.assertFalse(f.exists)

        f.delete()
        self.assertFalse(f.exists)
