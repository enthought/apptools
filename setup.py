#!/usr/bin/env python
#
# Copyright (c) 2008-2011 by Enthought, Inc.
# All rights reserved.

"""
ETS Application Tools

The AppTools project includes a set of packages that Enthought has found useful
in creating a number of applications. They implement functionality that is
commonly needed by many applications

- **enthought.appscripting**: Framework for scripting applications.
- **enthought.help**: Provides a plugin for displaying documents and examples
  and running demos in Envisage Workbench applications.
- **enthought.io**: Provides an abstraction for files and folders in a file
  system.
- **enthought.naming**: Manages naming contexts, supporting non-string data
  types and scoped preferences
- **enthought.permissions**: Supports limiting access to parts of an
  application unless the user is appropriately authorised (not full-blown
  security).
- **enthought.persistence**: Supports pickling the state of a Python object
  to a dictionary, which can then be flexibly applied in restoring the state of
  the object.
- **enthought.preferences**: Manages application preferences.
- **enthought.resource**: Manages application resources such as images and
  sounds.
- **enthought.scripting**: A framework for automatic recording of Python
  scripts.
- **enthought.sweet_pickle**: Handles class-level versioning, to support
  loading of saved data that exist over several generations of internal class
  structures.
- **enthought.template**: Supports creating templatizable object hierarchies.
- **enthought.type_manager**: Manages type extensions, including factories
  to generate adapters, and hooks for methods and functions.
- **enthought.undo**: Supports undoing and scripting application commands.

Prerequisites
-------------
If you want to build AppTools from source, you must first install
`setuptools <http://pypi.python.org/pypi/setuptools/0.6c8>`_ and
"""

from setuptools import setup, find_packages


# FIXME: This works around a setuptools bug which gets setup_data.py metadata
# from incorrect packages. Ticket #1592
#from setup_data import INFO
setup_data = dict(__name__='', __file__='setup_data.py')
execfile('setup_data.py', setup_data)
INFO = setup_data['INFO']


# Pull the description values for the setup keywords from our file docstring.
DOCLINES = __doc__.split("\n")

# The actual setup call.
setup(
    author = 'Enthought, Inc.',
    author_email = 'info@enthought.com',
    download_url = ('http://www.enthought.com/repo/ETS/AppTools-%s.tar.gz' %
                    INFO['version']),
    classifiers = [c.strip() for c in """\
        Development Status :: 5 - Production/Stable
        Intended Audience :: Developers
        Intended Audience :: Science/Research
        License :: OSI Approved :: BSD License
        Operating System :: MacOS
        Operating System :: Microsoft :: Windows
        Operating System :: OS Independent
        Operating System :: POSIX
        Operating System :: Unix
        Programming Language :: Python
        Topic :: Scientific/Engineering
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        """.splitlines() if len(c.strip()) > 0],
    description = DOCLINES[1],
    ext_modules = [],
    include_package_data = True,
    package_data = {'enthought': [
            'help/help_plugin/*.ini',
            'naming/ui/images/*.png',
            'help/help_plugin/action/images/*.png',
            ]},
    install_requires = INFO['install_requires'],
    license = 'BSD',
    long_description = '\n'.join(DOCLINES[3:]),
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    name = 'AppTools',
    namespace_packages = [
        "enthought",
        ],
    packages = find_packages(),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    tests_require = [
        'nose >= 0.10.3',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/projects/app_tools.php',
    version = INFO['version'],
    zip_safe = False,
)
