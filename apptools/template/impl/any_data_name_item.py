#-------------------------------------------------------------------------------
#
#  An abstract base class implementation of the ITemplateDataNameItem interface
#  that looks for all specified values in its input context or optionally any of
#  its sub-contexts and outputs a context containing all such values found.
#
#  Written by: David C. Morrill
#
#  Date: 07/29/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" An abstract base class implementation of the ITemplateDataNameItem interface
    that looks for all specified values in its input context or optionally any
    of its sub-contexts and outputs a context containing all such values found.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import HasPrivateTraits, Instance, Property, provides

from apptools.template.template_traits \
    import TBool

from apptools.template.itemplate_data_context \
    import ITemplateDataContext

from apptools.template.itemplate_data_name_item \
    import ITemplateDataNameItem

from apptools.template.template_impl \
    import Template

from .template_data_context \
    import TemplateDataContext

from .helper \
    import path_for

#-------------------------------------------------------------------------------
#  'AnyDataNameItem' class:
#-------------------------------------------------------------------------------

class AnyDataNameItem ( Template ):
    """ An abstract base class implementation of the ITemplateDataNameItem
        interface that looks for all specified values in its input context or
        optionally any of its sub-contexts and outputs a context containing all
        such values found.
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

    #-- Public Traits ----------------------------------------------------------

    # Should all sub-contexts be included in the search:
    recursive = TBool( False )

    # Should included sub-contexts be flattened into a single context?
    flatten = TBool( False )

    #-- Private Traits ---------------------------------------------------------

    # The current recursive setting:
    current_recursive = TBool( False )

    # The current input data context:
    current_input_data_context = Property

    #-- Abstract Methods (Must be overridden in subclasses) --------------------

    def filter ( self, name, value ):
        """ Returns **True** if the specified context data *name* and *value*
            should be included in the output context; and **False** otherwise.
        """
        raise NotImplementedError

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

    def _recursive_changed ( self, value ):
        """ Handles the primary recursive setting being changed.
        """
        self.current_recursive = value

    def _input_data_context_changed ( self ):
        """ Handles the 'input_data_context' trait being changed.
        """
        self.inputs_changed()

    #-- Private Methods --------------------------------------------------------

    def inputs_changed ( self ):
        """ Handles any input value being changed. This method should be called
            by subclasses when any of their input values change.
        """
        output_context = None
        input_context  = self.current_input_data_context
        if input_context is not None:
            values = {}

            if self.current_recursive:
                if self.flatten:
                    self._add_context( input_context, values )
                else:
                    self._copy_context( input_context, values )
            else:
                self._add_values(  input_context, values, '' )

            if len( values ) > 0:
                output_context = TemplateDataContext(
                    data_context_path = input_context.data_context_path,
                    data_context_name = input_context.data_context_name,
                    values            = values )

        self.output_data_context = output_context

    def _add_values ( self, input_context, values, path = '' ):
        """ Adds all of the matching values in the specified *input_context* to
            the specified *values* dictionary.
        """
        # Filter each name/value in the current input context to see if it
        # should be added to the output values:
        filter = self.filter
        gdcv   = input_context.get_data_context_value
        for name in input_context.data_context_values:
            value = gdcv( name )
            if self.filter( name, value ):
                values[ path_for( path, name ) ] = value

    def _add_context ( self, input_context, values, path = '' ):
        """ Adds all of the matching values in the specified *input_context* to
            the specified *output_context*, and then applies itself recursively
            to all contexts contained in the specified *input_context*.
        """
        # Add all of the filtered values in the specified input context:
        self._add_values( input_context, values, path )

        # Now process all of the input context's sub-contexts:
        gdc = input_context.get_data_context
        for name in input_context.data_contexts:
            self._add_context( gdc( name ), values, path_for( path,
                                            input_context.data_context_name ) )

    def _copy_context ( self, input_context ):
        """ Clone the input context so that the result only contains values and
            contexts which contain valid values and are not empty.
        """
        values   = {}
        contexts = {}

        # Add all of the filtered values in the specified input context:
        self._add_values( input_context, values )

        # Now process all of the input context's sub-contexts:
        gdc = input_context.get_data_context
        for name in input_context.data_contexts:
            context = self._copy_context( gdc( name ) )
            if context is not None:
                contexts[ name ] = context

        if (len( values ) == 0) and (len( contexts ) == 0):
            return None

        return TemplateDataContext(
                    data_context_path = input_context.data_context_path,
                    data_context_name = input_context.data_context_name,
                    values            = values,
                    contexts          = contexts )

