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
BLOCKCANVAS = etsdep('BlockCanvas', '3.1.1') # -- only used by enthought.template
CHACO = etsdep('Chaco', '3.2.1')  # -- only used by enthought.template
ENABLE = etsdep('Enable', '3.2.1')  # -- only used by enthought.template
ENTHOUGHTBASE = etsdep('EnthoughtBase', '3.0.4')
ENVISAGECORE = etsdep('EnvisageCore', '3.1.2')  # -- mostly in enthought.help, enthought.naming use is in a try..except
ENVISAGEPLUGINS = etsdep('EnvisagePlugins', '3.1.2')  # -- only used by enthought.help
ETSDEVTOOLS_DEVELOPER = etsdep('ETSDevTools[developer]', '3.0.4')  # -- only used by enthought.template
#MAYAVI -- not required due to the way state_pickler.py uses the import
TRAITSBACKENDWX = etsdep('TraitsBackendWX', '3.2.1')  # -- directly used only by enthought.template
TRAITSGUI = etsdep('TraitsGUI', '3.1.1')
TRAITSGUI_DOCK = etsdep('TraitsGUI[dock]', '3.1.1')  # -- only used by enthought.template
TRAITS_UI = etsdep('Traits[ui]', '3.2.1')


# A dictionary of the setup data information.
INFO = {
    'extras_require' : {
        "help": [
            ENVISAGECORE,
            ENVISAGEPLUGINS,
            ],
        'template': [
            BLOCKCANVAS,
            CHACO,
            ETSDEVTOOLS_DEVELOPER,
            ENABLE,
            TRAITSBACKENDWX,
            TRAITSGUI_DOCK,
            ],

        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            'configobj',
            'numpy',
            #'PyQt4', -- not everyone uses Qt.
            #'wxPython', -- not everyone uses WX.
            ],
        },
    'install_requires' : [
        ENTHOUGHTBASE,
        TRAITSGUI,
        TRAITS_UI,
        ],
    'name': 'AppTools',
    'version': '3.3.1',
    }

