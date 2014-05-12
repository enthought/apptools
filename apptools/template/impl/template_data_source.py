#-------------------------------------------------------------------------------
#
#  A concrete implementation of the ITemplateDataSource interface based on the
#  implementation of the TemplateDataName class.
#
#  Write by: David C. Morrill
#
#  Date: 07/30/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" A concrete implementation of the ITemplateDataSource interface based on the
    implementation of the TemplateDataName class.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import provides

from apptools.template.template_data_name \
    import TemplateDataName

from apptools.template.itemplate_data_source \
    import ITemplateDataSource

#-------------------------------------------------------------------------------
#  'TemplateDataSource' class:
#-------------------------------------------------------------------------------

class TemplateDataSource ( TemplateDataName ):
    """ A concrete implementation of the ITemplateDataSource interface based on
        the implementation of the TemplateDataName class.
    """

    implements( ITemplateDataSource )

    #-- ITemplateDataSource Interface Implementation ---------------------------

    def name_from_data_source ( self ):
        """ Allows the object to provide a description of the possibly optional
            data binding it requires.

            Returns
            -------
            A **TemplateDataName** object describing the binding the data
            source object requires.
        """
        return self

