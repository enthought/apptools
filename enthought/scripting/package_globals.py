"""
Globals for the scripting package.
"""
# Author: Prabhu Ramachandran <prabhu@aero.iitb.ac.in>
# Copyright (c) 2008, Prabhu Ramachandran and Enthought, Inc.
# License: BSD Style.


# The global recorder.
_recorder = None

def get_recorder():
    """Return the global recorder.  Does not create a new one if none
    exists.
    """
    global _recorder
    return _recorder

def set_recorder(rec):
    """Set the global recorder instance.
    """
    global _recorder
    _recorder = rec


