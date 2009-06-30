#------------------------------------------------------------------------------
# Copyright (c) 2008, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: Ilan Schnell, Enthought, Inc.
#
# Description:
#     Unittest to run another script directly.  In some cases this is
#     necessary when things cannot be tested with nosetests itself.
#------------------------------------------------------------------------------
import sys
import os.path
import subprocess
import unittest
import tempfile

from enthought.util.resource import store_resource, get_path


class Tests(unittest.TestCase):

    def setUp(self):
        OS_handle, fname = tempfile.mkstemp()
        os.close(OS_handle)
        self.tmpname = fname

    
    def test_file_path(self):
        """
            Run 'check_file_path.py' as a spawned process and test
            return value,
            The python source is stored into a temporary test file before
            being executed in a subprocess.
        """
        store_resource('AppTools',
                       os.path.join('enthought', 'persistence','tests',
                                    'check_file_path.py'),
                       self.tmpname)
        
        retcode = subprocess.call([sys.executable, self.tmpname],
                                  cwd=get_path(Tests))
        
        self.assertEqual(retcode, 0)


    def test_version_registry(self):
        """
            Run 'check_version_registry.py' as a spawned process and test
            return value,
            The python source is stored into a temporary test file before
            being executed in a subprocess.
        """
        store_resource('AppTools',
                       os.path.join('enthought', 'persistence','tests',
                                    'check_version_registry.py'),
                       self.tmpname)
        
        retcode = subprocess.call([sys.executable, self.tmpname])
        
        self.assertEqual(retcode, 0)


    def tearDown(self):
        os.unlink(self.tmpname)

if __name__ == "__main__":
    unittest.main()
