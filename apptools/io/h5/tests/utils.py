from contextlib import contextmanager
import tempfile
import os

from ..file import H5File


SEPARATOR = '-' * 60


@contextmanager
def open_h5file(filename, mode='r+', **kwargs):
    h5 = H5File(filename, mode=mode, **kwargs)
    try:
        yield h5
    finally:
        h5.close()


@contextmanager
def temp_file(suffix='', prefix='tmp', dir=None):
    fd, filename = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dir)
    try:
        yield filename
    finally:
        os.close(fd)
        os.unlink(filename)


@contextmanager
def temp_h5_file(**kwargs):
    with temp_file(suffix='h5') as fn:
        with open_h5file(fn, mode='a', **kwargs) as h5:
            yield h5
