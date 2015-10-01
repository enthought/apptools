===========================
apptools: application tools
===========================

.. image:: https://api.travis-ci.org/enthought/apptools.png?branch=master
   :target: https://travis-ci.org/enthought/apptools
   :alt: Build status

.. image:: http://codecov.io/github/enthought/apptools/coverage.svg?branch=master
   :target: http://codecov.io/github/enthought/apptools?branch=master
   :alt: Coverage report

Documentation: http://docs.enthought.com/apptools

Source Code: http://www.github.com/enthought/apptools


The apptools project includes a set of packages that Enthought has found
useful in creating a number of applications.  They implement functionality
that is commonly needed by many applications

- **apptools.appscripting**: Framework for scripting applications.
- **apptools.help**: Provides a plugin for displaying documents and examples
  and running demos in Envisage Workbench applications.
- **apptools.io**: Provides an abstraction for files and folders in a file
  system.
- **apptools.logger**: Convenience functions for creating logging handlers
- **apptools.naming**: Manages naming contexts, supporting non-string data
  types and scoped preferences
- **apptools.permissions**: Supports limiting access to parts of an
  application unless the user is appropriately authorised (not full-blown
  security).
- **apptools.persistence**: Supports pickling the state of a Python object
  to a dictionary, which can then be flexibly applied in restoring the state of
  the object.
- **apptools.preferences**: Manages application preferences.
- **apptools.selection**: Manages the communication between providers and
  listener of selected items in an application.
- **apptools.scripting**: A framework for automatic recording of Python
  scripts.
- **apptools.sweet_pickle**: Handles class-level versioning, to support
  loading of saved data that exist over several generations of internal class
  structures.
- **apptools.template**: Supports creating templatizable object hierarchies.
- **apptools.type_manager**: Manages type extensions, including factories
  to generate adapters, and hooks for methods and functions.
- **apptools.undo**: Supports undoing and scripting application commands.

Prerequisites
-------------

All packages in apptools require:

* `traits <https://github.com/enthought/traits>`_

The `apptools.preferences` package requires:

* `configobj <http://pypi.python.org/pypi/configobj>`_

Many of the packages provide optional user interfaces using Pyface and
Traitsui. In additon, many of the packages are designed to work with the
Envisage plug-in system, althought most can be used independently:

* `envisage <https://github.com/enthought/envisage>`_
* `pyface <https://github.com/enthought/pyface>`_
* `traitsui <https://github.com/enthought/traitsui>`_
