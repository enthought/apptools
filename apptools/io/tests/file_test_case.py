#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Enthought, Inc.
# Description: <Enthought IO package component>
#------------------------------------------------------------------------------
""" Tests file operations. """


# Standard library imports.
import os, shutil, stat, unittest

# Enthought library imports.
from apptools.io import File


class FileTestCase(unittest.TestCase):
    """ Tests file operations on a local file system. """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        try:
            shutil.rmtree('data')

        except:
            pass

        os.mkdir('data')

        return

    def tearDown(self):
        """ Called immediately after each test method has been called. """

        shutil.rmtree('data')

        return

    ###########################################################################
    # Tests.
    ###########################################################################

    def test_properties(self):
        """ file properties """

        # Properties of a non-existent file.
        f = File('data/bogus.xx')

        self.assert_(os.path.abspath(os.path.curdir) in f.absolute_path)
        self.assertEqual(f.children, None)
        self.assertEqual(f.ext, '.xx')
        self.assertEqual(f.exists, False)
        self.assertEqual(f.is_file, False)
        self.assertEqual(f.is_folder, False)
        self.assertEqual(f.is_package, False)
        self.assertEqual(f.is_readonly, False)
        self.assertEqual(f.mime_type, 'content/unknown')
        self.assertEqual(f.name, 'bogus')
        self.assertEqual(f.parent.path, 'data')
        self.assertEqual(f.path, 'data/bogus.xx')
        self.assert_(os.path.abspath(os.path.curdir) in f.url)
        self.assertEqual(str(f), 'File(%s)' % f.path)

        # Properties of an existing file.
        f = File('data/foo.txt')
        f.create_file()

        self.assert_(os.path.abspath(os.path.curdir) in f.absolute_path)
        self.assertEqual(f.children, None)
        self.assertEqual(f.ext, '.txt')
        self.assertEqual(f.exists, True)
        self.assertEqual(f.is_file, True)
        self.assertEqual(f.is_folder, False)
        self.assertEqual(f.is_package, False)
        self.assertEqual(f.is_readonly, False)
        self.assertEqual(f.mime_type, 'text/plain')
        self.assertEqual(f.name, 'foo')
        self.assertEqual(f.parent.path, 'data')
        self.assertEqual(f.path, 'data/foo.txt')
        self.assert_(os.path.abspath(os.path.curdir) in f.url)

        # Make it readonly.
        os.chmod(f.path, stat.S_IRUSR)
        self.assertEqual(f.is_readonly, True)

        # And then make it NOT readonly so that we can delete it at the end of
        # the test!
        os.chmod(f.path, stat.S_IRUSR | stat.S_IWUSR)
        self.assertEqual(f.is_readonly, False)

        return

    def test_copy(self):
        """ file copy """

        content = 'print "Hello World!"\n'

        f = File('data/foo.txt')
        self.assertEqual(f.exists, False)

        # Create the file.
        f.create_file(content)
        self.assertEqual(f.exists, True)
        self.assertRaises(ValueError, f.create_file, content)

        self.assertEqual(f.children, None)
        self.assertEqual(f.ext, '.txt')
        self.assertEqual(f.is_file, True)
        self.assertEqual(f.is_folder, False)
        self.assertEqual(f.mime_type, 'text/plain')
        self.assertEqual(f.name, 'foo')
        self.assertEqual(f.path, 'data/foo.txt')

        # Copy the file.
        g = File('data/bar.txt')
        self.assertEqual(g.exists, False)

        f.copy(g)
        self.assertEqual(g.exists, True)

        self.assertEqual(g.children, None)
        self.assertEqual(g.ext, '.txt')
        self.assertEqual(g.is_file, True)
        self.assertEqual(g.is_folder, False)
        self.assertEqual(g.mime_type, 'text/plain')
        self.assertEqual(g.name, 'bar')
        self.assertEqual(g.path, 'data/bar.txt')

        # Attempt to copy a non-existent file (should do nothing).
        f = File('data/bogus.xx')
        self.assertEqual(f.exists, False)

        g = File('data/bogus_copy.txt')
        self.assertEqual(g.exists, False)

        f.copy(g)
        self.assertEqual(g.exists, False)

        return

    def test_create_file(self):
        """ file creation """

        content = 'print "Hello World!"\n'

        f = File('data/foo.txt')
        self.assertEqual(f.exists, False)

        # Create the file.
        f.create_file(content)
        self.assertEqual(f.exists, True)
        self.assertEqual(open(f.path).read(), content)

        # Try to create it again.
        self.assertRaises(ValueError, f.create_file, content)

        return

    def test_delete(self):
        """ file deletion """

        content = 'print "Hello World!"\n'

        f = File('data/foo.txt')
        self.assertEqual(f.exists, False)

        # Create the file.
        f.create_file(content)
        self.assertEqual(f.exists, True)
        self.assertRaises(ValueError, f.create_file, content)

        self.assertEqual(f.children, None)
        self.assertEqual(f.ext, '.txt')
        self.assertEqual(f.is_file, True)
        self.assertEqual(f.is_folder, False)
        self.assertEqual(f.mime_type, 'text/plain')
        self.assertEqual(f.name, 'foo')
        self.assertEqual(f.path, 'data/foo.txt')

        # Delete it.
        f.delete()
        self.assertEqual(f.exists, False)

        # Attempt to delete a non-existet file (should do nothing).
        f = File('data/bogus.txt')
        self.assertEqual(f.exists, False)

        f.delete()
        self.assertEqual(f.exists, False)

        return

if __name__ == "__main__":
    unittest.main()

#### EOF ######################################################################
