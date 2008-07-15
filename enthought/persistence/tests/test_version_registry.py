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
#     Unittest to run another (unittest) script directly.
#     In some cases this is necessary when things cannot be tested
#     with nosetests itself.
#------------------------------------------------------------------------------
import os
import subprocess
import unittest

# NOTE:
#   `check_version_registry.py` can not be run by nosetests directly because of
#   namespace issues.   Therefore the test in this file (which nosetests
#   will execute) will spawn a python interpreter running the unittest.
#   This test checks the return code of the process and will fail if
#   the return code is non-zero.

class RefreshTestCase(unittest.TestCase):
    
    def test_run(self):
        cwd = os.path.dirname(__file__)
        if not cwd:
            cwd = '.'
        
        retcode = subprocess.call(['python', 'check_version_registry.py'],
                                  cwd=cwd)
        
        self.assertEqual(retcode, 0)
        

if __name__ == "__main__":          
    unittest.main()
