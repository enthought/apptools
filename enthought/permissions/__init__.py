#------------------------------------------------------------------------------
# Copyright (c) 2007 by Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
""" Supports limiting access to parts of an application to authorised users.
    Part of the AppTools project of the Enthought Tool Suite.
"""
try:
    __import__('pkg_resources').declare_namespace(__name__)
except:
    pass

# For py2app / py2exe support
try:
    import modulefinder
    for p in __path__:
        modulefinder.AddPackagePath(__name__, p)
except:
    pass
