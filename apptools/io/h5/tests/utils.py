from contextlib import contextmanager
import tempfile
import os

from ..utils import open_h5file


SEPARATOR = '-' * 60


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
