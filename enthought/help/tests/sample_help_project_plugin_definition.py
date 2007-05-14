from enthought.envisage.ui.ui_plugin_definition import Action, UIActions
from enthought.envisage.core.plugin_definition import PluginDefinition

from enthought.help.help_plugin_definition import HelpProject

###############################################################################
# Extensions.
###############################################################################

#### Help Project #############################################################

sample_help_project = HelpProject(
    proj_id = "enthought.help.tests.SampleHelpProject",
    name = "Sample",
    help_file = "../TestHelp/TestHelp.chm",
    map_file = "../TestHelp/BSSCDefault.h",
    custom_wnd = "Context",
)

# #### Menus/Actions ############################################################
# 

sample_help_project_action = Action(
    id        ="enthought.help.tests.SampleHelpProjectAction",
    class_name="enthought.help.tests.sample_help_action.SampleHelpProjectAction",
    name          = "Sample Help Project",
    image         = "",
    description   = "Sample Help Project",
    tooltip       = "Sample Help Project",
    menu_bar_path = "HelpMenu/",
    tool_bar_path = "",
)

sample_traits_help_action = Action(
    id  = "enthought.help.tests.SampleTraitsHelpAction",
    class_name  = "enthought.help.tests.sample_help_action.SampleTraitsHelpAction",
    name    = "Sample Traits Help",
    image   = "",
    description = "Sample Traits Help",
    tooltip = "Sample Traits Help",
    menu_bar_path = "HelpMenu/",
    tool_bar_path = "",
)

ui_actions = UIActions(
    actions = [
        sample_help_project_action,
        sample_traits_help_action,
    ]
)

###############################################################################
# The plugin definition
###############################################################################

PluginDefinition(
    # The plugin's globally unique identifier.
    id = "enthought.help.tests",
    
    # The name of the class that implements the plugin.
    class_name = "enthought.help.tests.sample_help_project_plugin.SampleHelpProjectPlugin",

    # General information about the plugin.
    name          = "Sample Help Project Plugin",
    version       = "1.0.0",
    provider_name = "Enthought Inc",
    provider_url  = "www.enthought.com",
    enabled       = True,
    autostart     = False,
    
    # The Id's of the plugins that this plugin requires.
    requires = ["enthought.envisage.ui", "enthought.help"],

    # The extension points offered by this plugin.
    extension_points = [],
    
    # The contributions that this plugin makes to extension points offered by
    # either itself or other plugins.
    extensions = [ui_actions, sample_help_project]
)

#### EOF ######################################################################
