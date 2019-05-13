#-------------------------------------------------------------------------------
#
#  A concrete base class that implements the IMutableTemplate interface.
#
#  Written by: David C. Morrill
#
#  Date: 08/01/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" A concrete base class that implements the IMutableTemplate interface.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import Event, provides

from .template_impl \
    import Template

from .imutable_template \
    import IMutableTemplate

#-------------------------------------------------------------------------------
#  'MutableTemplate' class:
#-------------------------------------------------------------------------------

class MutableTemplate ( Template ):
    """ A concrete base class that implements the IMutableTemplate interface.
    """

    implements( IMutableTemplate )

    #-- IMutableTemplate Interface Implementation ------------------------------

    # An event fired when the template mutates (i.e. changes in some way that
    # may affect the number of data sources it exposes, and so on):
    template_mutated = Event

