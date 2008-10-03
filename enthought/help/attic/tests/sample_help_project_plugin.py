from os.path import abspath, dirname, join
from enthought.envisage import Plugin

class SampleHelpProjectPlugin(Plugin):
    
    # The shared plugin instance.
    instance = None

    #### 'PreferencePlugin' interface #########################################
   
    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **kw):
        """ Creates a new plugin. """

        # Base-class constructor.
        Plugin.__init__(self, **kw)

        # Set the shared instance.
        SampleHelpProjectPlugin.instance = self
        
        return

    def start(self, application):
        pass
        
    def stop(self, application):
        pass
        
