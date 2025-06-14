# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
from contextlib import contextmanager

from .file import H5File


@contextmanager
def open_h5file(filename, mode="r+", **kwargs):
    """Context manager for reading an HDF5 file as an H5File object.

    Parameters
    ----------
    filename : str
        HDF5 file name.
    mode : str
        Mode to open the file:

        'r' : Read-only
        'w' : Write; create new file (an existing file would be deleted).
        'a' : Read and write to file; create if not existing
        'r+': Read and write to file; must already exist

    See `H5File` for additional keyword arguments.
    """
    h5 = H5File(filename, mode=mode, **kwargs)
    try:
        yield h5
    finally:
        h5.close()
