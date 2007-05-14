# Plugin definition imports.
from enthought.envisage.core.core_plugin_definition import PluginDefinition
   
from enthought.help.help_plugin_definition import HelpProject


enlib_help = HelpProject(
    proj_id = "enlib",
    name = "Enthought Library",
    help_file = "EnLibHelp.chm",
    map_file = "EnLibHelp/EnLibHelp.h",
    custom_wnd = "Context",
)

PluginDefinition(
    # The plugin's globally unique identifier.
    id = "enthought.help.enlib_help",

    # The name of the class that implements the plugin.
    class_name = "enthought.help.enlib_help_project_plugin.EnLibHelpProjectPlugin",

    # General information about the plugin.
    name          = "Enthought Library Help Plugin",
    version       = "1.0.0",
    provider_name = "Enthought Inc",
    provider_url  = "www.enthought.com",
    autostart     = True,
    enabled       = True,

    # The Id's of the plugins that this plugin requires.
    requires = [
        "enthought.help",
    ],

    # The extension points offered by this plugin.
    extension_points = [],
    
    # The contributions that this plugin makes to extension points offered by
    # either itself or other plugins.
    extensions = [enlib_help]
)


