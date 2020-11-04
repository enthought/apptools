#-------------------------------------------------------------------------------
#
#  Defines an adapter from an codetools.contexts.api.IContext
#  to an ITemplateDataContext.
#
#  Written by: David C. Morrill
#  Modified by: Robert Kern
#
#  Date: 11/16/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines an adapter from an codetools.contexts.api.IContext to an
    ITemplateDataContext.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import Adapter, Str, List, adapts

from traits.protocols.api \
    import AdaptationError, adapt

from codetools.contexts.api \
    import IContext

from apptools.template.itemplate_data_context \
    import ITemplateDataContext, ITemplateDataContextError

from .helper \
    import path_for

#-------------------------------------------------------------------------------
#  'IContextAdapter' class:
#-------------------------------------------------------------------------------

class IContextAdapter ( Adapter ):
    """ Defines an adapter from an codetools.contexts.api.IContext
        to an ITemplateDataContext.
    """

    adapts( IContext, ITemplateDataContext )

    #-- ITemplateDataContext Interface Implementation --------------------------

    # The path to this data context (does not include the 'data_context_name'):
    data_context_path = Str

    # The name of the data context:
    data_context_name = Str

    # A list of the names of the data values in this context:
    data_context_values = List( Str )

    # The list of the names of the sub-contexts of this context:
    data_contexts = List( Str )

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
            if name in self.data_context_values:
                return self.adaptee[ name ]

            raise ITemplateDataContextError(
                      "No value named '%s' found." % name )
        except Exception as excp:
            raise ITemplateDataContextError( str( excp ) )

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
            if name in self.data_contexts:
                bdca = IContextAdapter( self.adaptee[ name ] )
                bdca.data_context_path = path_for( self.data_context_path,
                                                   self.data_context_name )
                return bdca

            raise ITemplateDataContextError(
                      "No context named '%s' found." % name )
        except Exception as excp:
            raise ITemplateDataContextError( str( excp ) )

    #-- Traits Event Handlers --------------------------------------------------

    def _adaptee_changed ( self, context ):
        """ Handles being bound to a IContext object.
        """
        self.data_context_name = context.name
        values   = []
        contexts = []
        for name in context.keys():
            value = context[ name ]
            try:
                adapt( value, IContext )
            except AdaptationError:
                # Is not a subcontext.
                values.append( name )
            else:
                # Is a subcontext.
                contexts.append( name )

        self.data_context_values = values
        self.data_contexts       = contexts

