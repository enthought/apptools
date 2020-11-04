#-------------------------------------------------------------------------------
#
#  Defines the IMutableTemplate interface used to define modifiable templates.
#
#  Written by: David C. Morrill
#
#  Date: 08/01/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines the IMutableTemplate interface used to define modifiable templates.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import Event

from .itemplate \
    import ITemplate

#-------------------------------------------------------------------------------
#  'IMutableTemplate' interface:
#-------------------------------------------------------------------------------

class IMutableTemplate ( ITemplate ):
    """ Defines the IMutableTemplate interface used to define modifiable
        templates.

        Extends the ITemplate interface by supporting the ability for the
        template to modify itself.
    """

    # An event fired when the template mutates (i.e. changes in some way that
    # may affect the number of data sources it exposes, and so on):
    template_mutated = Event

