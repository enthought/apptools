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
BLOCKCANVAS = etsdep('BlockCanvas', '3.0.0b1') # -- only used by enthought.template
CHACO = etsdep('Chaco', '3.0.0b1')  # -- only used by enthought.template
DEVTOOLS = etsdep('DevTools', '3.0.0b1')  # -- only used by enthought.template
ENABLE = etsdep('Enable', '3.0.0b1')  # -- only used by enthought.template
ENTHOUGHTBASE = etsdep('EnthoughtBase', '3.0.0b1')
ENVISAGECORE = etsdep('EnvisageCore', '3.0.0b1')  # -- mostly in enthought.help, but one in enthought.naming
ENVISAGEPLUGINS = etsdep('EnvisagePlugins', '3.0.0b1')  # -- only used by enthought.help
#MAYAVI -- not required due to the way state_pickler.py uses the import
TRAITS = etsdep('Traits', '3.0.0b1')
TRAITSBACKENDWX = etsdep('TraitsBackendWX', '3.0.0b1')  # -- directly used only by enthought.template
TRAITSGUI = etsdep('TraitsGUI', '3.0.0b1')
TRAITSGUI_DOCK = etsdep('TraitsGUI[dock]', '3.0.0b1')  # -- only used by enthought.template


setup(
    author = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    dependency_links = [
        'http://code.enthought.com/enstaller/eggs/source',
        ],
    description = 'Application tools',
    extras_require = {
        "envisage": [
            ENVISAGECORE,
            ENVISAGEPLUGINS,
            ],
        'template': [
            BLOCKCANVAS,
            CHACO,
            DEVTOOLS,
            ENABLE,
            TRAITSBACKENDWX,
            TRAITSGUI_DOCK,
            ],

        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            'configobj',
            'numpy',
            #'PyQt4' -- not everyone uses Qt.
            ],
        },
    ext_modules = [],
    include_package_data = True,
    install_requires = [
        ENTHOUGHTBASE,
        TRAITS,
        TRAITSGUI,
        ],
    license = 'BSD',
    name = 'AppTools',
    namespace_packages = [
        "enthought",
        ],
    packages = find_packages(),
    tests_require = [
        'nose >= 0.9',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/ets',
    version = '3.0.0b1',
    zip_safe = False,
    )

