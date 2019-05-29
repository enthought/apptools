#-------------------------------------------------------------------------------
#
#  A concrete implementation of the ITemplateDataNameItem interface that looks
#  for a specified named value in its input context or optionally in any of its
#  sub-contexts and outputs a context containing only those values that match
#  the specified name.
#
#  Written by: David C. Morrill
#
#  Date: 07/29/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" A concrete implementation of the ITemplateDataNameItem interface that looks
    for a specified named value in its input context or optionally in any of its
    sub-contexts and outputs a context containing only those values that match
    the specified name.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import Bool

from apptools.template.template_traits \
    import TStr, TBool

from apptools.template.template_choice \
    import TemplateChoice

from apptools.template.itemplate_data_context \
    import ITemplateDataContext

from .any_data_name_item \
    import AnyDataNameItem

from .helper \
    import parse_name, path_for

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Value used to reset to the factory settings:
ResetChoice = '--<Reset>--'

#-------------------------------------------------------------------------------
#  'ValueDataNameItem' class:
#-------------------------------------------------------------------------------

class ValueDataNameItem ( AnyDataNameItem ):
    """ A concrete implementation of the ITemplateDataNameItem interface that
        looks for a specified named value in its input context or optionally in
        any of its sub-contexts and outputs a context containing only those
        values that match the specified name.
    """

    #-- Public Traits ----------------------------------------------------------

    # The name of the value to be matched:
    name = TStr

    # (Override) Should included sub-contexts be flattened into a single
    # context?
    flatten = True

    #-- Private Traits ---------------------------------------------------------

    # The current name of the value to be matched:
    current_name = TStr

    # The current name's last component:
    current_name_last = TStr

    # Should all possible choices be included?
    all_choices = Bool( True )

    #-- AnyDataNameItem Property Implementation Overrides ----------------------

    def _get_data_name_item_choice ( self ):
        return TemplateChoice( choice_value = self.current_name )

    def _set_data_name_item_choice ( self, choice ):
        if choice.choice_value == ResetChoice:
            self.current_recursive = self.recursive
            self.current_name      = self.name
            self.all_choices       = True
        else:
            self.current_recursive = False
            self.current_name      = choice.choice_value
            self.all_choices       = False

    def _get_data_name_item_choices ( self ):
        context = self.input_data_context
        if context is None:
            return []

        if not self.all_choices:
            output_context = self.output_data_context
            if output_context is not None:
                return [ TemplateChoice( choice_value = name )
                          for name in output_context.data_context_values ]

        return ([ TemplateChoice( choice_value = ResetChoice ) ] +
                self._get_choices( context ))

    def _get_current_input_data_context ( self ):
        context = self.input_data_context
        for name in parse_name( self.current_name )[:-1]:
            if name not in context.data_contexts:
                return None

            context = context.get_data_context( name )

        return context

    #-- Abstract Method Implementations ----------------------------------------

    def filter ( self, name, value ):
        """ Returns **True** if the specified context data *name* and *value*
            should be included in the output context; and **False** otherwise.
        """
        return (name == self.current_name_last)

    #-- Trait Event Handlers ---------------------------------------------------

    def _name_changed ( self, name ):
        """ Handles the 'name' trait being changed.
        """
        self.current_name = name

    def _current_name_changed ( self, name ):
        self.current_name_last = parse_name( name )[-1]
        self.inputs_changed()

    #-- Private Methods --------------------------------------------------------

    def _get_choices ( self, context, path = '' ):
        """ Returns the list of available user settings choices for the
            specified context.
        """
        choices = [ TemplateChoice( choice_value = path_for( path, name ) )
                    for name in context.data_context_values ]

        if self.recursive:
            # Now process all of the context's sub-contexts:
            gdc = context.get_data_context
            for name in context.data_contexts:
                choices.extend( self._get_choices( gdc( name ), path_for( path,
                                    context.data_context_name ) ) )

        return choices

