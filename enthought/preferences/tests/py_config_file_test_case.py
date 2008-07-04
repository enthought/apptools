""" Tests for Python-esque '.ini' files. """


# Standard library imports.
import os, tempfile, unittest

# Enthought library imports.
from py_config_file import PyConfigFile


class PyConfigFileTestCase(unittest.TestCase):
    """ Tests for Python-esque '.ini' files. """

    def filename_in_tempdir(self, filename):
        return os.path.join(self.directory, filename)

    def filename_in_localdir(self, filename):
        return os.path.join(os.path.abspath(os.path.dirname(__file__)),
            filename)

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        self.directory = tempfile.mkdtemp()
        
        return

    def tearDown(self):
        """ Called immediately after each test method has been called. """
        
        try:
            os.rmdir(self.directory)
        except OSError:
            pass
        return

    ###########################################################################
    # Tests.
    ###########################################################################

    def test_load_from_filename(self):
        """ load from filename """

        config = PyConfigFile(self.filename_in_localdir('py_config_example.ini'))

        self.assertEqual('blue', config['acme.ui']['bgcolor'])
        self.assertEqual(50, config['acme.ui']['width'])
        self.assertEqual(1.0, config['acme.ui']['ratio'])
        self.assertEqual(True, config['acme.ui']['visible'])
        self.assertEqual({'a' : 1, 'b' : 2}, config['acme.ui']['foo'])
        self.assertEqual([1, 2, 3, 4], config['acme.ui']['bar'])
        
        return

    def test_load_from_file(self):
        """ load from file """

        config = PyConfigFile(file(self.filename_in_localdir('py_config_example.ini')))

        self.assertEqual('blue', config['acme.ui']['bgcolor'])
        self.assertEqual(50, config['acme.ui']['width'])
        self.assertEqual(1.0, config['acme.ui']['ratio'])
        self.assertEqual(True, config['acme.ui']['visible'])
        self.assertEqual({'a' : 1, 'b' : 2}, config['acme.ui']['foo'])
        self.assertEqual([1, 2, 3, 4], config['acme.ui']['bar'])

        return

    def test_save(self):
        """ save """

        config = PyConfigFile(file(self.filename_in_localdir('py_config_example.ini')))

        self.assertEqual('blue', config['acme.ui']['bgcolor'])
        self.assertEqual(50, config['acme.ui']['width'])
        self.assertEqual(1.0, config['acme.ui']['ratio'])
        self.assertEqual(True, config['acme.ui']['visible'])
        self.assertEqual({'a' : 1, 'b' : 2}, config['acme.ui']['foo'])
        self.assertEqual([1, 2, 3, 4], config['acme.ui']['bar'])

        # Save the config to another file.
        config.save(self.filename_in_tempdir('tmp.ini'))
        try:
            self.assert_(os.path.exists(self.filename_in_tempdir('tmp.ini')))

            # Make sure we can read the file back in and that we get the same
            # values!
            config = PyConfigFile(file(self.filename_in_tempdir('tmp.ini')))

            self.assertEqual('blue', config['acme.ui']['bgcolor'])
            self.assertEqual(50, config['acme.ui']['width'])
            self.assertEqual(1.0, config['acme.ui']['ratio'])
            self.assertEqual(True, config['acme.ui']['visible'])
            self.assertEqual({'a' : 1, 'b' : 2}, config['acme.ui']['foo'])
            self.assertEqual([1, 2, 3, 4], config['acme.ui']['bar'])

        finally:
            # Clean up!
            os.remove(self.filename_in_tempdir('tmp.ini'))

        return

    def test_load_multiple_files(self):
        """ load multiple files """

        config = PyConfigFile(self.filename_in_localdir('py_config_example.ini'))

        self.assertEqual('blue', config['acme.ui']['bgcolor'])
        self.assertEqual(50, config['acme.ui']['width'])
        self.assertEqual(1.0, config['acme.ui']['ratio'])
        self.assertEqual(True, config['acme.ui']['visible'])
        self.assertEqual({'a' : 1, 'b' : 2}, config['acme.ui']['foo'])
        self.assertEqual([1, 2, 3, 4], config['acme.ui']['bar'])

        # Load another file.
        config.load(self.filename_in_localdir('py_config_example_2.ini'))

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
