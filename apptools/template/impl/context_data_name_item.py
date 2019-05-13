#-------------------------------------------------------------------------------
#
#  A concrete implementation of the ITemplateDataNameItem interface that looks
#  for a specified sub-context in its input context and outputs that as its
#  output context if it is found.
#
#  Written by: David C. Morrill
#
#  Date: 07/29/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" A concrete implementation of the ITemplateDataNameItem interface that looks
    for a specified sub-context in its input context and outputs that as its
    output context if it is found.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from apptools.template.template_traits \
    import TStr

from .any_context_data_name_item \
    import AnyContextDataNameItem

from .helper \
    import path_for, parse_name

#-------------------------------------------------------------------------------
#  'ContextDataNameItem' class:
#-------------------------------------------------------------------------------

class ContextDataNameItem ( AnyContextDataNameItem ):
    """ A concrete implementation of the ITemplateDataNameItem interface that
        looks for a specified sub-context in its input context and outputs that
        as its output context if it is found.
    """

    #-- Public Traits ----------------------------------------------------------

    # The name of the context to be matched:
    name = TStr

    #-- Abstract Method Implementations ----------------------------------------

    def filter ( self, name, context ):
        """ Returns **True** if the specified *context* called *name* should be
            included in the output context; and **False** otherwise.
        """
        return (name == self.name_last)

    #-- AnyDataNameItem Property Implementation Overrides ----------------------

    def _get_data_name_item_choice ( self ):
        return TemplateChoice( choice_value = self.name )

    def _set_data_name_item_choice ( self, value ):
        self.name = value.choice_value

    def _get_data_name_item_choices ( self ):
        return self._get_choices( self.input_data_context )

    def _get_current_input_data_context ( self ):
        context = self.input_data_context
        for name in parse_name( self.name )[:-1]:
            if name not in context.data_contexts:
                return None

            context = context.get_data_context( name )

        return context

    #-- Trait Event Handlers ---------------------------------------------------

    def _name_changed ( self, name ):
        """ Handles the 'name' trait being changed.
        """
        self.name_last = parse_name( name )[-1]
        self.inputs_changed()

    #-- Private Methods --------------------------------------------------------

    def _get_choices ( self, context, path = '' ):
        """ Returns all of the valid TemplateChoices for this item.
        """
        choices = []
        gdc     = context.get_data_context
        for name in context.data_contexts:
            next_path = path_for( path, name )
            choices.append( TemplateChoice( choice_value = next_path ) )
            choices.extend( self._get_choices( gdc( name ), next_path ) )

        return choices

