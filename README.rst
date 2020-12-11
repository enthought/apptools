===========================
apptools: application tools
===========================

.. image:: https://travis-ci.org/enthought/apptools.svg?branch=master
    :target: https://travis-ci.org/enthought/apptools
    :alt: Build status

Documentation: http://docs.enthought.com/apptools

Source Code: http://www.github.com/enthought/apptools


The apptools project includes a set of packages that Enthought has found
useful in creating a number of applications.  They implement functionality
that is commonly needed by many applications

- **apptools.io**: Provides an abstraction for files and folders in a file
  system.
- **apptools.logger**: Convenience functions for creating logging handlers
- **apptools.naming**: Manages naming contexts, supporting non-string data
  types and scoped preferences
- **apptools.persistence**: Supports pickling the state of a Python object
  to a dictionary, which can then be flexibly applied in restoring the state of
  the object.
- **apptools.preferences**: Manages application preferences.
- **apptools.selection**: Manages the communication between providers and
  listener of selected items in an application.
- **apptools.scripting**: A framework for automatic recording of Python
  scripts.
- **apptools.undo**: Supports undoing and scripting application commands.

Prerequisites
-------------

All packages in apptools require:

* `traits <https://github.com/enthought/traits>`_

Certain sub-packages within apptools have their own specific dependencies,
which are optional for apptools overall.

The `apptools.preferences` package requires:

* `configobj <http://pypi.python.org/pypi/configobj>`_

The `apptools.io.h5` package requires:

* `numpy <https://pypi.org/project/numpy/>`_
* `pandas <https://pypi.org/project/pandas/>`_
* `tables <https://pypi.org/project/tables/>`_

The `apptools.persistence` package requires:

* `numpy <https://pypi.org/project/numpy/>`_

Many of the packages provide optional user interfaces using Pyface and
Traitsui. In additon, many of the packages are designed to work with the
Envisage plug-in system, althought most can be used independently:

* `envisage <https://github.com/enthought/envisage>`_
* `pyface <https://github.com/enthought/pyface>`_
* `traitsui <https://github.com/enthought/traitsui>`_

Installation
------------

To install with `apptools.preferences` dependencies::

    $ pip install apptools[preferences]

To install with `apptools.io.h5` dependencies::

    $ pip install apptools[h5]

To install with `apptools.persistence` dependencies::

    $ pip install apptools[persistence]

To install with additional test dependencies::

    $ pip install apptools[test]
