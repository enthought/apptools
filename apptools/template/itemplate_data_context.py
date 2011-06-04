#-------------------------------------------------------------------------------
#
#  Defines the ITemplateDataContext interface for accessing a named collection
#  of data that can be bound to a templatized object when converting it to a
#  'live' set of objects.
#
#  Written by: David C. Morrill
#
#  Date: 07/26/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines the ITemplateDataContext interface for accessing a named collection
    of data that can be bound to a templatized object when converting it to a
    'live' set of objects.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api\
    import Interface, List, Str

#-------------------------------------------------------------------------------
#  'ITemplateDataContext' interface:
#-------------------------------------------------------------------------------

class ITemplateDataContext ( Interface ):
    """ Defines the ITemplateDataContext interface for accessing a named
        collection of data that can be bound to a templatized object when
        converting it to a 'live' set of objects.
    """

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

#-------------------------------------------------------------------------------
#  'ITemplateDataContextError' exception:
#-------------------------------------------------------------------------------

class ITemplateDataContextError ( Exception ):
    """ The exception class associated with the **ITemplateDataContext**
        interface.
    """

