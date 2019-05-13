#-------------------------------------------------------------------------------
#
#  A concrete implementation of the ITemplateDataNameItem interface that looks
#  for array values of a specified dimensionality in its input context or
#  optionally in any of its sub-contexts and outputs a context containing
#  only those values that it found.
#
#  Written by: David C. Morrill
#
#  Date: 07/29/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" A concrete implementation of the ITemplateDataNameItem interface that looks
    for array values of a specified dimensionality in its input context or
    optionally in any of its sub-contexts and outputs a context containing
    only those values that it found.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from numpy \
    import array

from apptools.template.template_traits \
    import TRange

from apptools.template.template_choice \
    import TemplateChoice

from .any_data_name_item \
   import AnyDataNameItem

#-------------------------------------------------------------------------------
#  'ValueNDDataNameItem' class:
#-------------------------------------------------------------------------------

class ValueNDDataNameItem ( AnyDataNameItem ):
    """ A concrete implementation of the ITemplateDataNameItem interface that
        looks for array values of a specified dimensionality in its input
        context or optionally in any of its sub-contexts and outputs a context
        containing only those values that it found.
    """

    #-- Public Traits ----------------------------------------------------------

    # The dimensionality of the array values to be accepted:
    dimensions = TRange( 0, 1000 )

    #-- AnyDataNameItem Property Implementation Overrides ----------------------

    def _get_data_name_item_choice ( self ):
        return TemplateChoice( choice_value = '%dD array' % self.dimensions )

    def _set_data_name_item_choice ( self, value ):
        pass

    def _get_data_name_item_choices ( self ):
        return []

    #-- Abstract Method Implementations ----------------------------------------

    def filter ( self, name, value ):
        """ Returns **True** if the specified context data *name* and *value*
            should be included in the output context; and **False** otherwise.
        """
        return (isinstance( value, array ) and
                (len( value.shape ) == self.dimensions ))

    #-- Trait Event Handlers ---------------------------------------------------

    def _name_changed ( self ):
        """ Handles the 'name' trait being changed.
        """
        self.inputs_changed()

#-------------------------------------------------------------------------------
#  Define a few common sub-classes for 1D, 2D and 3D arrays:
#-------------------------------------------------------------------------------

class Value1DDataNameItem ( ValueNDDataNameItem ):

    # Override the dimensionaly of the array values to be accepted:
    dimensions = 1

class Value2DDataNameItem ( ValueNDDataNameItem ):

    # Override the dimensionaly of the array values to be accepted:
    dimensions = 2

class Value3DDataNameItem ( ValueNDDataNameItem ):

    # Override the dimensionaly of the array values to be accepted:
    dimensions = 3

