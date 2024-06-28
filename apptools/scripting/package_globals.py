# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
"""
Globals for the scripting package.
"""


# The global recorder.
_recorder = None


def get_recorder():
    """Return the global recorder.  Does not create a new one if none
    exists.
    """
    global _recorder
    return _recorder


def set_recorder(rec):
    """Set the global recorder instance."""
    global _recorder
    _recorder = rec
