#-------------------------------------------------------------------------------
#
#  An abstract base class implementation of the ITemplateDataNameItem interface
#  that looks for specified sub-contexts in its input context and if one match
#  is found, outputs that context; otherwise if more than one match is found it
#  outputs a context containing all matching sub-contexts found.
#
#  Written by: David C. Morrill
#
#  Date: 07/29/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" An abstract base class implementation of the ITemplateDataNameItem interface
    that looks for specified sub-contexts in its input context and if one match
    is found, outputs that context; otherwise if more than one match is found it
    outputs a context containing all matching sub-contexts found.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import HasPrivateTraits, Instance, Property, provides, on_trait_change

from apptools.template.itemplate_data_context \
    import ITemplateDataContext

from apptools.template.itemplate_data_name_item \
    import ITemplateDataNameItem

from apptools.template.template_impl \
    import Template

from .template_data_context \
    import TemplateDataContext

#-------------------------------------------------------------------------------
#  'AnyContextDataNameItem' class:
#-------------------------------------------------------------------------------

class AnyContextDataNameItem ( Template ):
    """ An abstract base class implementation of the ITemplateDataNameItem
        interface that looks for specified sub-contexts in its input context
        and if one match is found, outputs that context; otherwise if more than
        one match is found it outputs a context containing all matching
        sub-contexts found.
    """

    implements ( ITemplateDataNameItem )

    #-- 'ITemplateDataNameItem' Interface Implementation -----------------------

    # The data context which this data name item should match against:
    input_data_context = Instance( ITemplateDataContext )

    # The data context containing the data values and/or contexts this data
    # name item matches:
    output_data_context = Instance( ITemplateDataContext )

    # The ITemplateChoice instance representing the current settings of the
    # data name item. This value must be read/write, and must be overridden by
    # sublasses.
    data_name_item_choice = Property

    # The alternative choices the user has for the data name item settings for
    # the current input data context. The list may be empty, in which case the
    # user cannot change the settings of the data name item. This value can be
    # read only, and must be overridden by subclasses.
    data_name_item_choices = Property

    #-- Private Traits ---------------------------------------------------------

    # The current input data context:
    current_input_data_context = Property

    #-- Partially Abstract Methods (Can be overridden in subclasses) -----------

    def filter ( self, name, context ):
        """ Returns **True** if the specified *context* called *name* should be
            included in the output context; and **False** otherwise.
        """
        return False

    #-- Property Implementations -----------------------------------------------

    def _get_data_name_item_choice ( self ):
        raise NotImplementedError

    def _set_data_name_item_choice ( self, value ):
        raise NotImplementedError

    def _get_data_name_item_choices ( self ):
        raise NotImplementedError

    def _get_current_input_data_context ( self ):
        return self.input_data_context

    #-- Trait Event Handlers ---------------------------------------------------

    def _input_data_context_changed ( self ):
        """ Handles the 'input_data_context' trait being changed.
        """
        self.inputs_changed()

    #-- Private Methods --------------------------------------------------------

    def inputs_changed ( self ):
        """ Handles any of the input values being changed. May be called by
            subclasses.
        """
        output_context = None
        input_context  = self.input_data_context
        if input_context is not None:
            contexts = {}

            # Process each name/context in the input data contexts, and only add
            # those that match the subclass's filter to the output context:
            filter = self.filter
            gdc    = input_context.get_data_context
            for name in input_context.data_contexts:
                if filter( name, gdc( name ) ):
                    contexts[ name ] = context

            # If the result set is not empty, create an output context for it:
            n = len( contexts )
            if n == 1:
                output_context = list(values.values())[0]
            elif n > 1:
                output_context = TemplateDataContext(
                    data_context_path = input_context.data_context_path,
                    data_context_name = input_context.data_context_name,
                    contexts          = contexts )

        # Set the new output context:
        self.output_data_context = output_context

