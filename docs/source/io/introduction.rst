File I/O
========

The :mod:`apptools.io` package provides a traited |File| object provides
properties and methods for common file path manipulation operations.  Much of
this functionality was implemented before Python 3 `pathlib`_ standard library
became available to provide similar support.  For new code we encourage users
to investigate if `pathlib`_ can satisfy their use cases before they turn to
the `apptools.io` |File| object

HDF5 File Support
-----------------

The :mod:`apptools.io.h5` sub-package provides a wrapper around `PyTables`_
with a dictionary-style mapping.


..
   external links

.. _pathlib: https://docs.python.org/3/library/pathlib.html
.. _PyTables: https://www.pytables.org/


..
   # substitutions

.. |File| replace:: :class:`~apptools.io.file.File`
