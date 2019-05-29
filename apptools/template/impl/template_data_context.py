#-------------------------------------------------------------------------------
#
#  A concrete implementation of the ITemplateDataContext interface intended to
#  be used for creating the *output_data_context* value of an
#  **ITemplateDataNameItem** implementation (although they are not required to
#  use it).
#
#  Written by: David C. Morrill
#
#  Date: 07/29/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" A concrete implementation of the ITemplateDataContext interface intended to
    be used for creating the *output_data_context* value of an
    **ITemplateDataNameItem** implementation (although they are not required to
    use it).
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api\
    import HasPrivateTraits, Dict, Str, Any, Property, provides, \
           cached_property

from apptools.template.itemplate_data_context \
    import ITemplateDataContext, ITemplateDataContextError

#-------------------------------------------------------------------------------
#  'TemplateDataContext' class:
#-------------------------------------------------------------------------------

class TemplateDataContext ( HasPrivateTraits ):
    """ A concrete implementation of the ITemplateDataContext interface
        intended to be used for creating the *output_data_context* value of an
        **ITemplateDataNameItem** implementation (although they are not
        required to use it).
    """

    implements( ITemplateDataContext )

    #-- 'ITemplateDataContext' Interface Traits --------------------------------

    # The path to this data context (does not include the 'data_context_name'):
    data_context_path = Str

    # The name of the data context:
    data_context_name = Str

    # A list of the names of the data values in this context:
    data_context_values = Property # List( Str )

    # The list of the names of the sub-contexts of this context:
    data_contexts = Property # List( Str )

    #-- Public Traits ---------------------------------------------------------

    # The data context values dictionary:
    values = Dict( Str, Any )

    # The data contexts dictionary:
    contexts = Dict( Str, ITemplateDataContext )

    #-- 'ITemplateDataContext' Property Implementations ------------------------

    @cached_property
    def _get_data_context_values ( self ):
        values = sorted(self.values.keys())
        return values

    @cached_property
    def _get_data_contexts ( self ):
        contexts = sorted(self.contexts.keys())
        return contexts

    #-- 'ITemplateDataContext' Interface Implementation ------------------------

    def get_data_context_value ( self, name ):
        """ Returns the data value with the specified *name*. Raises a
            **ITemplateDataContextError** if *name* is not defined as a data
            value in the context.

            Parameters
            ----------
            name : A string specifying the name of the context data value to
                be returned.

            Returns
            -------
            The data value associated with *name* in the context. The type of
            the data is application dependent.

            Raises **ITemplateDataContextError** if *name* is not associated
            with a data value in the context.
        """
        try:
            return self.values[ name ]
        except:
            raise ITemplateDataContextError( "Value '%s' not found." % name )

    def get_data_context ( self, name ):
        """ Returns the **ITemplateDataContext** value associated with the
            specified *name*. Raises **ITemplateDataContextError** if *name* is
            not defined as a data context in the context.

            Parameters
            ----------
            name : A string specifying the name of the data context to be
                returned.

            Returns
            -------
            The **ITemplateDataContext** associated with *name* in the context.

            Raises **ITemplateDataContextError** if *name* is not associated
            with a data context in the context.
        """
        try:
            return self.context[ name ]
        except:
            raise ITemplateDataContextError( "Context '%s' not found." % name )

