#-------------------------------------------------------------------------------
#
#  Defines the ITemplateDataSource interface for creating 'live' application
#  data sources from a templatized data source object.
#
#  Written by: David C. Morrill
#
#  Date: 07/26/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines the ITemplateDataSource interface for creating 'live' application
    data sources from a templatized data source object.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import Interface

#-------------------------------------------------------------------------------
#  'ITemplateDataSource' interface:
#-------------------------------------------------------------------------------

class ITemplateDataSource ( Interface ):
    """ Defines the ITemplateDataSource interface for creating 'live'
        application data sources from a templatized data source object.
    """

    def name_from_data_source ( self ):
        """ Allows the object to provide a description of the possibly optional
            data binding it requires.

            Returns
            -------
            A **TemplateDataName** object describing the binding the data
            source object requires.
        """

