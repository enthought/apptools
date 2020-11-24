io
===

The io package provides a traited |File| object provides properties and methods
for common file path manipulation operations.  On Python 3 much of this
functionality is provided by the `pathlib`_ module, and for new code we
encourage users to investigate if `pathlib`_ can satisfy their usecase before
they turn to the `apptools.io` |File| object

io.h5
-----
The io.h5 sub-package provides a wrapper around `PyTables`_ with a
dictionary-style mapping.  Note that this module has a decent amount of
overlap with `zarr`_.

..
   external links

.. _pathlib: https://docs.python.org/3/library/pathlib.html
.. _PyTables: https://www.pytables.org/
.. _zarr: https://zarr.readthedocs.io/en/stable/


..
   # substitutions

.. |File| replace:: :class:`~apptools.io.file.File`
