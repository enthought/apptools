from os.path import abspath, dirname, join
from enthought.envisage import Plugin

class EnLibHelpProjectPlugin(Plugin):
    
    # The shared plugin instance.
    instance = None

    #### 'Plugin' interface #########################################
   
    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **kw):
        """ Creates a new plugin. """

        # Base-class constructor.
        Plugin.__init__(self, **kw)

        # Set the shared instance.
        EnLibHelpProjectPlugin.instance = self
        
        return

#### EOF ######################################################################        
