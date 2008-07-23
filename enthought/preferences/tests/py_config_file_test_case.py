""" Tests for Python-esque '.ini' files. """


# Standard library imports.
import os, tempfile, unittest
from os.path import join

# Major package imports.
from pkg_resources import resource_filename

# Enthought library imports.
from py_config_file import PyConfigFile


# This module's package.
PKG = 'enthought.preferences.tests'


class PyConfigFileTestCase(unittest.TestCase):
    """ Tests for Python-esque '.ini' files. """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        # The filename of the example preferences file.
        self.example = resource_filename(PKG, 'py_config_example.ini')
        self.example_2 = resource_filename(PKG, 'py_config_example_2.ini')
        
        return

    def tearDown(self):
        """ Called immediately after each test method has been called. """
        
        return

    ###########################################################################
    # Tests.
    ###########################################################################

    def test_load_from_filename(self):
        """ load from filename """

        config = PyConfigFile(self.example)

        self.assertEqual('blue', config['acme.ui']['bgcolor'])
        self.assertEqual(50, config['acme.ui']['width'])
        self.assertEqual(1.0, config['acme.ui']['ratio'])
        self.assertEqual(True, config['acme.ui']['visible'])
        self.assertEqual({'a' : 1, 'b' : 2}, config['acme.ui']['foo'])
        self.assertEqual([1, 2, 3, 4], config['acme.ui']['bar'])
        
        return

    def test_load_from_file(self):
        """ load from file """

        config = PyConfigFile(file(self.example))

        self.assertEqual('blue', config['acme.ui']['bgcolor'])
        self.assertEqual(50, config['acme.ui']['width'])
        self.assertEqual(1.0, config['acme.ui']['ratio'])
        self.assertEqual(True, config['acme.ui']['visible'])
        self.assertEqual({'a' : 1, 'b' : 2}, config['acme.ui']['foo'])
        self.assertEqual([1, 2, 3, 4], config['acme.ui']['bar'])

        return

    def test_save(self):
        """ save """

        config = PyConfigFile(file(self.example))

        self.assertEqual('blue', config['acme.ui']['bgcolor'])
        self.assertEqual(50, config['acme.ui']['width'])
        self.assertEqual(1.0, config['acme.ui']['ratio'])
        self.assertEqual(True, config['acme.ui']['visible'])
        self.assertEqual({'a' : 1, 'b' : 2}, config['acme.ui']['foo'])
        self.assertEqual([1, 2, 3, 4], config['acme.ui']['bar'])

        # Save the config to another file.
        tmpdir = tempfile.mkdtemp()
        
        tmp = join(tmpdir, 'tmp.ini')
        config.save(tmp)
        try:
            self.assert_(os.path.exists(tmp))

            # Make sure we can read the file back in and that we get the same
            # values!
            config = PyConfigFile(file(tmp))

            self.assertEqual('blue', config['acme.ui']['bgcolor'])
            self.assertEqual(50, config['acme.ui']['width'])
            self.assertEqual(1.0, config['acme.ui']['ratio'])
            self.assertEqual(True, config['acme.ui']['visible'])
            self.assertEqual({'a' : 1, 'b' : 2}, config['acme.ui']['foo'])
            self.assertEqual([1, 2, 3, 4], config['acme.ui']['bar'])

        finally:
            # Clean up!
            os.remove(tmp)
            os.removedirs(tmpdir)

        return

    def test_load_multiple_files(self):
        """ load multiple files """

        config = PyConfigFile(self.example)

        self.assertEqual('blue', config['acme.ui']['bgcolor'])
        self.assertEqual(50, config['acme.ui']['width'])
        self.assertEqual(1.0, config['acme.ui']['ratio'])
        self.assertEqual(True, config['acme.ui']['visible'])
        self.assertEqual({'a' : 1, 'b' : 2}, config['acme.ui']['foo'])
        self.assertEqual([1, 2, 3, 4], config['acme.ui']['bar'])

        # Load another file.
        config.load(self.example_2)

        # Make sure we still have the unchanged values...
        self.assertEqual('red', config['acme.ui']['bgcolor'])
        self.assertEqual(50, config['acme.ui']['width'])
        self.assertEqual(1.0, config['acme.ui']['ratio'])
        self.assertEqual(True, config['acme.ui']['visible'])
        self.assertEqual({'a' : 1, 'b' : 2}, config['acme.ui']['foo'])
        self.assertEqual([1, 2, 3, 4], config['acme.ui']['bar'])

        # ... and the values that were overwritten...
        self.assertEqual('red', config['acme.ui']['bgcolor'])

        # ... and that we have the new ones.
        self.assertEqual(42, config['acme.ui']['bazzle'])
        
        return

# Entry point for stand-alone testing.
if __name__ == '__main__':
    unittest.main()

#### EOF ######################################################################
