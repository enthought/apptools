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
# Author: Prabhu Ramachandran
# Description: Automatic script recording framework.
#------------------------------------------------------------------------------

"""Automatic script recording framework, part of the AppTools project
   of the Enthought Tool Suite.
"""
__import__('pkg_resources').declare_namespace(__name__)

# For py2app / py2exe support
try:
    import modulefinder
    for p in __path__:
        modulefinder.AddPackagePath(__name__, p)
except:
    pass
