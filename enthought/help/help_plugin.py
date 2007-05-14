""" A plug-in that manages help projects for other plug-ins. """


# Standard library imports.
from os.path import abspath, basename, join
from shutil import copy
import sys

# Enthought library imports.
from enthought.envisage import Plugin
from enthought.logger import logger
from enthought.pyface.api import ImageResource
from enthought.traits.api import Instance, Function
from enthought.traits.ui.help import on_help_call

# Local imports.
from helplibrary import helplibrary
from robohelp_csh import is_html_help, is_web_help

# Plugin imports.
from help_plugin_definition import HelpProject


# The IDs of the services this plug-in offers.
IHELP    = 'enthought.help.IHelp'


class HelpPlugin(Plugin):
    """ A plug-in that manages help projects for other plug-ins. """

    # The shared plugin instance.
    _instance = None
    # The implementation instance
    library = None
    # Image for toolbar icons
    help_image = Instance(ImageResource, ImageResource('help_action'))
    # Default Traits help handler
    traits_help_handler = Function
    

    #### 'HelpPlugin' interface ###############################################
    def traits_show_help(self, info, control):
        """ Function to show help for Traits-based views."""
        # print "in traits_show_help()"
        help_id_to_show = ""
        
        # If there's a help_id on the view, use it.
        if info.ui.view.help_id != "":
            help_id_to_show = info.ui.view.help_id
        else:
            # Use the first help_id found, if any, on the view's elements
            help_ids = []
            view_conts = info.ui.view_elements.content
            for element in view_conts.keys():
                if view_conts[element].help_id != "":
                    help_id_to_show = view_conts[element].help_id
                    break
                    
        # If there's a help_id, show its topic
        # print "help_id_to_show: %s" % help_id_to_show
        if help_id_to_show != "":
            logger.debug("Showing help topic: %s" % help_id_to_show)
            self.library.show_topic(help_id_to_show)
            
        else:
            # No help_id, so call the default Traits help handler instead
            self.traits_help_handler(info, control)
        return
    
    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **kw):
        """ Creates a new plug-in. """

        # Base-class constructor.
        super(HelpPlugin, self).__init__(**kw)

        # Set the shared instance.
        HelpPlugin._instance = self
        
        return
        
    ###########################################################################
    # 'Plugin' interface.
    ###########################################################################

    def start(self, application):
        """ Starts the plug-in.

        Called exactly once when the plug-in is first required.

        """
        # print "In HelpPlugin.start()"
        
        self._replace_traits_help_handler()
        self._add_extensions_to_library()
        self.register_service(IHELP, self._instance)
        
        return
    
    def stop(self, application):
        """ Stops the plug-in.

        Called exactly once when either the plug-in is manually stopped or the
        application exits.

        """
        return
        
    ###########################################################################
    # 'Private' interface.
    ###########################################################################
        
    def _replace_traits_help_handler(self):
        # Save the original Traits help handler
        self.traits_help_handler = on_help_call()
        # print "Saved help handler is: %s" % self.traits_help_handler
        
        # Replace with this plug-in's handler for Traits help
        on_help_call(self.traits_show_help) 
        # print "New help handler is %s" % on_help_call()
 
    def _add_extensions_to_library(self):
        # Get the global help library
        HelpPlugin.library = helplibrary()
        
        # Get all contributions to the HelpProject extension point.
        extensions = self.get_extensions(HelpProject)
        # print "Extensions to HelpProject: %s" % extensions
        for extension in extensions:
            # print "** Processing HelpProject: %s" % extension.name
            ext_location = extension._definition_.location
            # print "\t Location: %s" % ext_location
            if extension.help_file != "":
                help_file = basename(extension.help_file)
                help_file = self._add_help_file_extension(help_file)
                #if using_chm == True:
                #    # Copy to state location
                #    dst_help_file = join(self.state_location, help_file)
                #    copy(join(ext_location, extension.help_file), self.state_location)
                #else: # Assume it's WebHelp; run from installed location.
                dst_help_file = abspath(join(ext_location, extension.help_file))
            else:
                dst_help_file = None

            dst_map_file = None
            if extension.map_file != "":
                map_file = basename(extension.map_file)
                #if is_html_help(help_file):
                #    dst_map_file = join(self.state_location, map_file)
                #    copy(join(ext_location, extension.map_file), self.state_location)
                #else:
                dst_map_file = abspath(join(ext_location, extension.map_file))

            # Add all help projects to the global help library
            HelpPlugin.library.add_helpproject(
                extension.proj_id, 
                dst_help_file, 
                dst_map_file,
                custom_wnd=extension.custom_wnd
            )
        
    def _add_help_file_extension(self, help_filename):
        """ Adds a file extension if there is not one already. 
        
        On MS Windows, it adds '.chm'; otherwise, it adds '.htm' 
        (for WebHelp).
        
        """
        filename = help_filename
        if not (is_html_help(help_filename)) and not (is_web_help(help_filename)):
            if sys.platform == 'win32':
                filename = help_filename + '.chm'
            else:
                filename = help_filename + '.htm'
        return filename
            
#### EOF ######################################################################
