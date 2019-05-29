#-------------------------------------------------------------------------------
#
#  Defines the TemplateDataNames class used to manage application data source
#  bindings to named context data.
#
#  Written by: David C. Morrill
#
#  Date: 07/26/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines the TemplateDataNames class used to manage application data source
    bindings to named context data.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import HasPrivateTraits, Instance, Int, List, Property, Delegate, \
           cached_property

from traitsui.api \
    import View, Item, TableEditor, EnumEditor, TextEditor

from traitsui.table_column \
    import ObjectColumn

from .template_data_name \
    import TemplateDataName

from .itemplate_data_context \
    import ITemplateDataContext

from .template_choice \
    import TemplateChoice

#-------------------------------------------------------------------------------
#  Table editor support for editing a list of TemplateDataName objects:
#-------------------------------------------------------------------------------

class BindingsColumn ( ObjectColumn ):

    # The column index:
    index = Int

    #-- ObjectColumn Method Overrides ------------------------------------------

    def is_editable ( self, object ):
        return (self.index < len( object.data_name.items ))

    def get_editor ( self, object ):
        return EnumEditor( values =
             [ dnic.choice_value for dnic in object.data_name.items[
                                         self.index ].data_name_item_choices ] +
             [ self.get_raw_value( object ) ] )

class ResolvedColumn ( ObjectColumn ):

    def get_raw_value( self, object ):
        if object.data_name.resolved:
            return ''

        return 'X'

    def get_cell_color ( self, object ):
        if object.data_name.resolved:
            return self.read_only_cell_color_

        return self.cell_color_

class OptionalColumn ( ObjectColumn ):

    def get_raw_value( self, object ):
        return ' X'[ object.data_name.optional ]

# Define the table editor:
table_editor = TableEditor(
    columns_name       = 'table_columns',
    configurable       = False,
    auto_size          = False,
    sortable           = False,
    scroll_dy          = 4,
    selection_bg_color = None
)

# The standard columns:
std_columns = [
    ResolvedColumn( name     = 'resolved',
                    label    = '?',
                    editable = False,
                    width    = 20,
                    horizontal_alignment = 'center',
                    cell_color = 0xFF8080 ),
    OptionalColumn( name     = 'optional',
                    label    = '*',
                    editable = False,
                    width    = 20,
                    horizontal_alignment = 'center' ),
    ObjectColumn(   name     = 'description',
                    editor   = TextEditor(),
                    width    = 0.47 ) ]

#-------------------------------------------------------------------------------
#  'TemplateDataNames' class:
#-------------------------------------------------------------------------------

class TemplateDataNames ( HasPrivateTraits ):

    #-- Public Traits ----------------------------------------------------------

    # The data context to which bindings are made:
    context = Instance( ITemplateDataContext )

    # The current set of data names to be bound to the context:
    data_names = List( TemplateDataName )

    # The list of unresolved, required bindings:
    unresolved_data_names = Property( depends_on = 'data_names.resolved' )

    # The list of optional bindings:
    optional_data_names = Property( depends_on = 'data_names.optional' )

    # The list of unresolved optional bindings:
    unresolved_optional_data_names = Property(
        depends_on = 'data_names.[resolved,optional]' )

    #-- Private Traits ---------------------------------------------------------

    # List of 'virtual' data names for use by table editor:
    virtual_data_names = List

    # The list of table editor columns:
    table_columns = Property( depends_on = 'data_names' ) # List( ObjectColumn )

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        Item( 'virtual_data_names',
              show_label = False,
              style      = 'custom',
              editor     = table_editor )
    )

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_unresolved_data_names ( self ):
        return [ dn for dn in self.data_names
                 if (not dn.resolved) and (not dn.optional) ]

    @cached_property
    def _get_optional_data_names ( self ):
        return [ dn for dn in self.data_names if dn.optional ]

    @cached_property
    def _get_unresolved_optional_data_names ( self ):
        return [ dn for dn in self.data_names
                 if (not dn.resolved) and dn.optional ]

    @cached_property
    def _get_table_columns ( self ):
        n =  max( [ len( dn.items ) for dn in self.data_names ] )
        if n == 1:
            return std_columns + [ BindingsColumn( name  = 'value0',
                                                   label = 'Name',
                                                   width = 0.43 ) ]
        width = 0.43 / n
        return (std_columns +
                [ BindingsColumn( name = 'value%d' % i,
                                 index = i,
                                 label = 'Name %d' % ( i + 1 ),
                                 width = width ) for i in range( n ) ])

    #-- Trait Event Handlers ---------------------------------------------------

    def _context_changed ( self, context ):
        for data_name in self.data_names:
            data_name.context = context

    def _data_names_changed ( self, old, new ):
        """ Handles the list of 'data_names' being changed.
        """
        # Make sure that all of the names are unique:
        new = set( new )

        # Update the old and new context links:
        self._update_contexts( old, new )

        # Update the list of virtual names based on the new set:
        dns = [ VirtualDataName( data_name = dn ) for dn in new ]
        dns.sort( lambda l, r: cmp( l.description, r.description ) )
        self.virtual_data_names = dns

    def _data_names_items_changed ( self, event ):
        # Update the old and new context links:
        old, new = event.old, event.new
        self._update_contexts( old, new )

        # Update the list of virtual names based on the old and new sets:
        i = event.index
        self.virtual_data_names[ i: i + len( old ) ] = [
            VirtualDataName( data_name = dn ) for dn in new ]

    #-- Private Methods --------------------------------------------------------

    def _update_contexts ( self, old, new ):
        """ Updates the data context for an old and new set of data names.
        """
        for data_name in old:
            data_name.context = None

        context = self.context
        for data_name in new:
            data_name.context = context

#-------------------------------------------------------------------------------
#  'VirtualDataName' class:
#-------------------------------------------------------------------------------

# Define the 'VirtualValue' property:
def _get_virtual_data ( self, name ):
    return self.data_name.items[
               self.trait( name ).index ].data_name_item_choice.choice_value

def _set_virtual_data ( self, name, new_value ):
    old_value = _get_virtual_data( self, name )
    if old_value != new_value:
        self.data_name.items[
                 self.trait( name ).index ].data_name_item_choice = \
            TemplateChoice( choice_value = new_value )

        self.trait_property_changed( name, old_value, new_value )

VirtualValue = Property( _get_virtual_data, _set_virtual_data )

class VirtualDataName ( HasPrivateTraits ):

    # The TemplateDataName this is a virtual copy of:
    data_name = Instance( TemplateDataName )

    # The data name description:
    description = Delegate( 'data_name', modify = True )

    # The 'virtual' traits of this object:
    value0 = VirtualValue( index = 0 )
    value1 = VirtualValue( index = 1 )
    value2 = VirtualValue( index = 2 )
    value3 = VirtualValue( index = 3 )
    value4 = VirtualValue( index = 4 )
    value5 = VirtualValue( index = 5 )

