"""Simple class to support file path objects that work well in the
context of persistent storage with the state_pickler.

"""
# Author: Prabhu Ramachandran <prabhu_r@users.sf.net>
# Copyright (c) 2005, Enthought, Inc.
# License: BSD Style.

# Standard library imports.
import os
from os.path import abspath, normpath, dirname, commonprefix, join


class FilePath(object):
    """This class stores two paths to the file.  A relative path and
    an absolute one.  The absolute path is used by the end user.  When
    this object is pickled the state_pickler sets the relative path
    relative to the file that is being generated.  When unpickled, the
    stored relative path is used to set the absolute path correctly
    based on the path of the saved file.
    """
    def __init__(self, value=''):
        self.set(value)

    def __str__(self):
        return self.abs_pth

    def __repr__(self):
        return self.abs_pth.__repr__()

    def get(self):
        """Get the path.
        """
        return self.abs_pth

    def set(self, value):
        """Sets the value of the path.
        """
        self.rel_pth = value
        if value:
            self.abs_pth = normpath(abspath(value))
        else:
            self.abs_pth = ''

    def set_relative(self, base_f_name):
        """Sets the path relative to `base_f_name`.  Note that
        `base_f_name` and self.rel_pth should be valid file names
        correct on the current os.  The set name is a file name that
        has a POSIX path.
        """

        # Get normalized paths.
        _src = abspath(base_f_name)
        _dst = self.abs_pth

        # Now strip out any common prefix between the two paths.
        for part in _src.split(os.sep):
            if _dst.startswith(part+os.sep):
                length = len(part) + 1
                _src = _src[length:]
                _dst = _dst[length:]
            else:
                break

        # For each directory in the source, we need to add a reference to
        # the parent directory to the destination.
        ret = (_src.count(os.sep) * ('..' + os.sep)) + _dst

        # Make it posix style.
        if os.sep is not '/':
            ret.replace(os.sep, '/')

        # Store it.
        self.rel_pth = ret

    def set_absolute(self, base_f_name):
        """Sets the absolute file name for the current relative file
        name with respect to the given `base_f_name`.
        """
        base_f_name = normpath(abspath(base_f_name))
        rel_file_name = normpath(self.rel_pth)
        file_name = join(dirname(base_f_name), rel_file_name)
        file_name = os.path.normpath(file_name)
        self.abs_pth = file_name

