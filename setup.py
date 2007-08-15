from setuptools import setup, find_packages


# Function to convert simple ETS project names and versions to a requirements
# spec that works for both development builds and stable builds.  Allows
# a caller to specify a max version, which is intended to work along with
# Enthought's standard versioning scheme -- see the following write up:
#    https://svn.enthought.com/enthought/wiki/EnthoughtVersionNumbers
def etsdep(p, min, max=None, literal=False):
    require = '%s >=%s.dev' % (p, min)
    if max is not None:
        if literal is False:
            require = '%s, <%s.a' % (require, max)
        else:
            require = '%s, <%s' % (require, max)
    return require


# Declare our ETS project dependencies.
ENVISAGE = etsdep('enthought.envisage', '2.0b1')
LOGGER = etsdep('enthought.envisage', '2.0b1')
PYFACE = etsdep('enthought.pyface', '2.0b1')
TRAITS_UI = etsdep('enthought.traits[ui]', '2.0b1')


setup(
    author = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    dependency_links = [
        'http://code.enthought.com/enstaller/eggs/source',
        'http://code.enthought.com/enstaller/eggs/source/unstable',
        ],
    description = 'Help framework for envisage applications',
    extras_require = {
        "plugin": [
            ENVISAGE,
            ],

        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            ],
        },
    include_package_data = True,
    install_requires = [
        LOGGER,
        PYFACE,
        TRAITS_UI,
        ],
    license = 'BSD',
    name = 'enthought.help',
    namespace_packages = [
        "enthought",
        ],
    packages = find_packages(),
    tests_require = [
        'nose >= 0.9',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/ets',
    version = '3.0.0a1',
    zip_safe = False,
    )

