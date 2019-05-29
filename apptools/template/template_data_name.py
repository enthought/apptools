#-------------------------------------------------------------------------------
#
#  Defines the TemplateDataName class used for binding a data source to a data
#  context.
#
#  Written by: David C. Morrill
#
#  Date: 07/27/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines the TemplateDataName class used for binding a data source to a data
    context.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import HasPrivateTraits, Instance, Bool, Property, Undefined, \
           on_trait_change, cached_property

from .itemplate_data_name_item \
    import ITemplateDataNameItem

from .itemplate_data_context \
    import ITemplateDataContext

from .template_impl \
    import Template

from .template_traits \
    import TList, TStr, TBool

#-------------------------------------------------------------------------------
#  'TemplateDataName' interface:
#-------------------------------------------------------------------------------

class TemplateDataName ( Template ):
    """ Defines the TemplateDataName class used for binding a data source to a
        data context.
    """

    #-- Public Template Traits -------------------------------------------------

    # The list of ITemplateDataNameItem's used to match the data context:
    items = TList( ITemplateDataNameItem )

    # A description of the template data name (for use in a user interface):
    description = TStr

    # Is this binding optional?
    optional = TBool( False )

    #-- Public Non-Template Traits ---------------------------------------------

    # The data context the template name is matching against currently:
    context = Instance( ITemplateDataContext )

    # Is the binding resolved?
    resolved = Property( Bool, depends_on = 'items.output_data_context' )

    # The actual name of the context data that the data source is bound to:
    context_data_name = Property

    # The context data the data source is bound to:
    context_data = Property

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_resolved ( self ):
        if len( self.items ) == 0:
            return False

        context = self.items[-1].output_data_context
        return ((context is not None) and
                (len( context.data_context_values ) == 1) and
                (len( context.data_contexts ) == 0))

    def _get_context_data_name ( self ):
        if self.resolved:
            context = self.items[-1].output_data_context
            path    = context.data_context_path
            if path != '':
                path += '.'
            name = context.data_context_name
            if name != '':
                name += '.'

            return '%s%s%s' % ( path, name, context.data_context_values[0] )

        return ''

    def _get_context_data ( self ):
        if self.resolved:
            context = self.items[-1].output_data_context
            return context.get_data_context_value(
                       context.data_context_values[0] )

        return Undefined

    #-- Trait Event Handlers ---------------------------------------------------

    def _context_changed ( self, context ):
        """ Resets the name whenever the context is changed.
        """
        self._reset()

    @on_trait_change( ' items' )
    def _on_items_changed ( self ):
        """ Resets the name whenever any of the name items are changed.
        """
        self._reset()

    @on_trait_change( 'items:output_data_context' )
    def _on_output_data_context_changed ( self, item, name, old, new ):
        i = self.items.index( item )
        if i < (len( self.items ) - 1):
            self.items[ i + 1 ].input_data_context = new

    #-- Private Methods --------------------------------------------------------

    def _reset ( self ):
        """ Resets the name whenever any significant change occurs.
        """
        items = self.items
        n     = len( items )
        if n > 0:
            items[0].input_data_context = self.context
            for i in range( 0, n - 1 ):
                items[ i + 1 ].input_data_context = \
                    items[ i ].output_data_context

