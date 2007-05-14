""" A plug-in that manages help projects for other plug-ins. """


# Enthought library imports.
from enthought.traits.api import List, Str

# Plugin definition imports.
from enthought.envisage.core.core_plugin_definition import ExtensionItem, ExtensionPoint, PluginDefinition


###############################################################################
# Extension points.
###############################################################################

#### Help projects #########################################################

class HelpProject(ExtensionPoint):
    """ A help project. 
    
    Can be an HTML Help (.chm) or WebHelp project.
    *Note:* There should be one HelpProject per help project per application. 
    If a plug-in needs a help project for which there is already a HelpProject
    defined in another plug-in, the former should "require" the latter, rather
    than redefining the HelpProject.
    """
    
    # The project's unique identifier.
    # Used in topic strings for context-sensitive help.
    proj_id = Str
    
    # The text to use in the Help menu
    # For now: help projects are responsible for adding themselves to the menu.
    name = Str

    # The file name of the project entry point. If a file extension is not
    # specified, the plug-in will append '.chm' on MS Windows and '.htm' 
    # otherwise.
    help_file = Str

    # The name of the .h file that maps topic IDs to map numbers.
    map_file = Str

    # The name of the custom window used for context-sensitive topic.
    # fixme?: Assumes that at most one custom window is used.
    custom_wnd = Str


# class HelpLib(ExtensionPoint):
    # """ Allows for contributions to the help library. """
# 
    # # Help project contributions.
    # projects = List(HelpProject)
    
###############################################################################
# Extensions.
###############################################################################

#### Help Projects ############################################################


# help_lib = HelpLib(
    # projects = []
# )
###############################################################################
# The plugin definition
###############################################################################

PluginDefinition(
    # The plugin's globally unique identifier.
    id = "enthought.help",
    
    # The name of the class that implements the plugin.
    class_name = "enthought.help.help_plugin.HelpPlugin",

    # General information about the plugin.
    name          = "Enthought Help Plugin",
    version       = "1.0.0",
    provider_name = "Enthought Inc",
    provider_url  = "www.enthought.com",
    enabled       = True,
    autostart     = True,
    
    # The IDs of the plugins that this plugin requires.
    requires = [],

    # The extension points offered by this plugin.
    extension_points = [HelpProject],
    
    # The contributions that this plugin makes to extension points offered by
    # either itself or other plugins.
    extensions = []
)

#### EOF ######################################################################
