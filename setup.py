# Copyright (c) 2008-2012 by Enthought, Inc.
# All rights reserved.
from os.path import join
from setuptools import setup, find_packages


info = {}
execfile(join('apptools', '__init__.py'), info)


setup(
    name = 'apptools',
    version = info['__version__'],
    author = 'Enthought, Inc.',
    author_email = 'info@enthought.com',
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    url = 'https://github.com/enthought/apptools',
    download_url = ('http://www.enthought.com/repo/ets/apptools-%s.tar.gz' %
                    info['__version__']),
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
    description = 'application tools',
    long_description = open('README.rst').read(),
    include_package_data = True,
    package_data = dict(apptools=[
            'help/help_plugin/*.ini',
            'help/help_plugin/action/images/*.png',
            'logger/plugin/*.ini',
            'logger/plugin/view/images/*.png',
            'naming/ui/images/*.png',
    ]),
    install_requires = info['__requires__'],
    license = 'BSD',
    packages = find_packages(),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    zip_safe = False,
)
