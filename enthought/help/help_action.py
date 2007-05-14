""" Executes a help command. """


# Enthought library imports.
from enthought.envisage import get_application
from enthought.traits.api import Instance

# FIXME: Support for both UI and Workbench plug-ins. When UI plug-in goes away,
# delete this crazy import stuff!
from enthought.envisage import using_workbench
if not using_workbench:
    from enthought.envisage.ui import WorkbenchAction
else:
    from enthought.envisage.workbench.action import WorkbenchAction


class HelpAction(WorkbenchAction):
    """ Abstract class for help actions. """
    plugin = Instance
    
    def __init__( self, **kw ):
        """ Constructor. """
    
        # Base-class constructor.
        WorkbenchAction.__init__(self, **kw)
        self.plugin = get_application().get_service('enthought.help.IHelp')
        # print "Initializing HelpAction"
        if kw.has_key('image'):
            self.image = kw['image']
        else: 
            self.image    = self.plugin.help_image

class HelpContentsAction(HelpAction):
    """ Displays the TOC for a help project. """
           
    ###########################################################################
    # 'Action' interface.
    ###########################################################################

    def perform(self, event = None):
        """ Performs the action. """
        # print "Performing HelpContentsAction"
        self.plugin.library.show_toc(self.id)

        return

class HelpTopicAction(HelpAction):
    """ Displays a topic for a Help Project. """


    ###########################################################################
    # 'Action' interface.
    ###########################################################################

    def perform(self):
        """ Performs the action. """
        self.plugin.library.show_topic(self.id)

        return

class HelpViewAction(HelpAction):
    """ Displays a topic for a view. """
    ###########################################################################
    # 'Action' interface.
    ###########################################################################

    def perform(self, event):
        """ Performs the action. """
        from enthought.envisage.workbench.services import IWORKBENCH
        
        wb = get_application().get_service(IWORKBENCH)
        ae = wb.active_window.active_editor
        print "Active Editor is: %s" % ae
        #self.plugin.library.show_topic(self.id)

        return
        
#### EOF ######################################################################
