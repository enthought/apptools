""" Utility functions for help plugin actions.

    :Copyright: 2008, Enthought Inc.
    :License: BSD
    :Author: Janet Swisher
"""
# This software is provided without warranty under the terms of the BSD
# license included in AppTools/trunk/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!

from os.path import isabs, join, normpath
import sys

def get_sys_prefix_relative_filename(filename):
    return None if (filename is None) else \
           filename if isabs(filename) else \
           normpath(join(sys.prefix, filename))
