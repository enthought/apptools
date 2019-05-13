#-------------------------------------------------------------------------------
#
#  A feature-based Traits UI plug-in for viewing templates.
#
#  Written by: David C. Morrill
#
#  Date: 07/30/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" A feature-based Traits UI plug-in for viewing templates.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys

from os.path \
    import split, splitext

from pickle \
    import dump, load

from traits.api \
    import HasPrivateTraits, Str, Instance, Any, File, Button, on_trait_change

from traitsui.api \
    import View, VGroup, HGroup, Tabbed, Item, InstanceEditor, Theme, Label

from traitsui.wx.themed_text_editor \
    import ThemedTextEditor

from etsdevtools.developer.features.api \
    import DropFile

from pyface.api \
    import FileDialog, OK

from etsdevtools.developer.helper.themes \
    import TButton

from blockcanvas.app.utils \
    import import_log_files

from apptools.template.api \
    import ITemplate, ITemplateDataContext, TemplateDataNames, Template

from .enable_editor \
    import EnableEditor

#-- Adapters that might be used ------------------------------------------------

from apptools.template.impl.base_data_context_adapter \
    import BaseDataContextAdapter

#-------------------------------------------------------------------------------
#  Helper class:
#-------------------------------------------------------------------------------

class Message ( HasPrivateTraits ):

    #-- Trait Definitions ------------------------------------------------------

    # The message to be displayed:
    message = Str

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        Item( 'message',
              style      = 'readonly',
              show_label = False,
              editor     = ThemedTextEditor( theme = '@GBB' ),
        )
    )

    #-- Object Overrides -------------------------------------------------------

    def __init__ ( self, message = '', **traits ):
        traits.setdefault( 'message', message )

        super( Message, self ).__init__( **traits )

# Define some standard messages:
no_context        = Message( 'Please provide a data context' )
no_template       = Message( 'Please provide a view template' )
no_template_found = Message( 'No view templates found in Python source file' )
no_bindings       = Message( 'Please resolve all required template data bindings' )
no_options        = Message( 'No options are currently available' )

#-------------------------------------------------------------------------------
#  'TemplateView' class:
#-------------------------------------------------------------------------------

class TemplateView ( HasPrivateTraits ):
    """ A feature-based Traits UI plug-in for viewing templates.
    """

    #-- Public Traits ----------------------------------------------------------

    # The name of the plugin:
    name = Str( 'Template View' )

    # The data context supplying the data to be viewed:
    context = Instance( ITemplateDataContext,
                        connect = 'to: data context' )

    # The name of the file containing a template view:
    file_name = File( drop_file = DropFile(
                     extensions = [ '.py', '.tv', '.las' ],
                     tooltip = 'Drop a LAS data file, a saved view template '
                               'or a Python source file containing a view '
                               'template here.' ),
                     connect = 'to: template view' )

    # The template to view:
    template = Instance( ITemplate )

    #-- Private Traits ---------------------------------------------------------

    # The name of the file to save the template in:
    save_file_name = File

    # The current data names:
    data_names = Instance( TemplateDataNames )

    # The TemplateDataNames or Message being viewed:
    names_view = Any( no_context )

    # The name of the most recently loaded template file:
    template_file_name = File

    # The template or message being viewed:
    template_view = Any( no_template )

    # The options view for the currently active template:
    options_view = Any( no_options )

    # The event fired when the user wants to save the template:
    save_template = Button( 'Save Template' )

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        VGroup(
            HGroup(
                Item( 'file_name', show_label = False, width = 350 ),
                TButton( 'save_template',
                      label        = 'Save Template',
                      enabled_when = 'template is not None' ),
                group_theme = Theme( '@GFB', margins = ( -7, -5 ) )
            ),
            Tabbed(
                VGroup(
                    '8',
                    Label( 'Data Bindings',
                           item_theme = Theme( '@GBB', alignment = 'center' )
                    ),
                    Item( 'names_view',
                          style      = 'custom',
                          resizable  = True,
                          editor     = InstanceEditor(),
                          export     = 'DockWindowShell',
                          item_theme = Theme( '@GFB', margins = ( -5, -1 ) )
                    ),
                    label       = 'Data Bindings',
                    show_labels = False
                ),
                Item( 'template_view',
                      label     = 'Template View',
                      style     = 'custom',
                      resizable = True,
                      editor    = InstanceEditor( view = 'template_view' ),
                      export    = 'DockWindowShell'
                ),
                Item( 'options_view',
                      label     = 'Template Options',
                      style     = 'custom',
                      resizable = True,
                      editor    = InstanceEditor( view = 'options_view' ),
                      export    = 'DockWindowShell'
                ),
                id          = 'tabbed',
                dock        = 'horizontal',
                show_labels = False
            ),
        ),
        id = 'template.test.template_view.TemplateView'
    )

    #-- Trait Event Handlers ---------------------------------------------------

    def _context_changed ( self, context ):
        """ Handles the 'context' trait being changed.
        """
        if context is None:
            self.names_view = no_context
        elif self.template is None:
            self.names_view = no_template
        else:
            self._create_view()

    def _template_changed ( self, template ):
        """ Handles the 'template' trait being changed.
        """
        if self.context is None:
            self.template_view = no_context
        else:
            self._create_view()

    def _file_name_changed ( self, file_name ):
        """ Handles the 'file_name' trait being changed.
        """
        ext = splitext( file_name )[1]
        if ext == '.py':
            self._load_python_template( file_name )
        elif ext == '.tv':
            self._load_pickled_template( file_name )
        elif ext == '.las':
            self._load_las_file( file_name )
        else:
            # fixme: Display an informational message here...
            pass

    def _save_template_changed ( self ):
        """ Handles the user clicking the 'Save Template' button.
        """
        self._save_pickled_template()

    @on_trait_change( 'data_names.unresolved_data_names' )
    def _on_unresolved_data_names ( self ):
        if len( self.data_names.unresolved_data_names ) == 0:
            self._create_object_view()
        elif not isinstance( self.template_view, Message ):
            self.template_view = no_bindings
            self.options_view  = no_options

    @on_trait_change( 'template.template_mutated?' )
    def _on_template_mutated ( self ):
        """ Handles a mutable template changing.
        """
        if self.context is not None:
            self._create_view()

    #-- Private Methods --------------------------------------------------------

    def _load_python_template ( self, file_name ):
        """ Attempts to load a template from a Python source file.
        """
        path, name    = split( file_name )
        sys.path[0:0] = [ path ]
        try:
            ###values = {}
            module_name, ext = splitext( name )
            module = __import__( module_name )
            values = module.__dict__
            ###execfile( file_name, values )
            template = values.get( 'template' )
            if template is None:
                templates = []
                for value in values.values():
                    try:
                        if (issubclass( value, Template ) and
                            ###(value.__module__ == '__builtin__')):
                            (value.__module__ == module_name)):
                            templates.append( value )
                    except:
                        pass

                for i, template in enumerate( templates ):
                    for t in templates[ i + 1: ]:
                        if issubclass( template, t ):
                            break
                    else:
                        break
                else:
                    self.template_view = no_template_found
                    return

            if not isinstance( template, Template ):
                template = template()

            self.template           = template
            self.template_file_name = file_name

        except Exception as excp:
            self.template_view = Message( str( excp ) )

        # Clean up the Python path:
        del sys.path[0]

    def _load_pickled_template ( self, file_name ):
        """ Attempts to load a template from a pickle.
        """
        # fixme: Implement this...load template from .tv pickle file.
        fh     = None
        delete = False
        try:
            fh            = open( file_name, 'rb' )
            file_name     = load( fh )
            path, name    = split( file_name )
            sys.path[0:0] = [ path ]
            delete        = True
            module_name, ext = splitext( name )
            module = __import__( module_name )
            self.template = load( fh )
            self.template_file_name = file_name
        except Exception as excp:
            import traceback
            traceback.print_exc()
            self.template_view = Message( str( excp ) )

        if fh is not None:
            fh.close()

        if delete:
            del sys.path[0]

    def _load_las_file ( self, file_name ):
        """ Creates a data context from the specified LAS file.
        """
        try:
            self.context = import_log_files( file_name, 'las' )
        except Exception as excp:
            self.names_view = Message( str( excp ) )

    def _save_pickled_template ( self ):
        file_name = self.save_file_name or self.file_name
        fd        = FileDialog(
                        action       = 'save as',
                        default_path = file_name )
                        #wildcard     = 'Template files (*.tv)|*.tv|' )
        if fd.open() == OK:
            self.save_file_name = file_name = fd.path
            fh = None
            try:
                fh = open( file_name, 'wb' )
                dump( self.template_file_name, fh, -1 )
                dump( self.template.template_from_object(), fh, -1 )
            except:
                # fixme: Display an informational message here...
                import traceback
                traceback.print_exc()

            if fh is not None:
                fh.close()

    def _create_view ( self ):
        """ Begins the process of creating a live view from a template and
            data context object.
        """
        self.data_names = self.names_view = nv = TemplateDataNames(
                              context    = self.context,
                              data_names = self.template.names_from_template() )

        if len( nv.unresolved_data_names ) == 0:
            self._create_object_view()
        else:
            self.template_view = no_bindings

    def _create_object_view ( self ):
        """ Create the object view from the current template.
        """
        self.template.object_from_template()
        self.template_view = self.options_view = self.template

