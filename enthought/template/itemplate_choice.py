#-------------------------------------------------------------------------------
#
#  Defines the ITemplateChoice interface used by ITemplateDataNameItem
#  interface.
#
#  Written by: David C. Morrill
#
#  Date: 07/29/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines the ITemplateChoice interface used by ITemplateDataNameItem
    interface.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import Interface, Str

#-------------------------------------------------------------------------------
#  'ITemplateChoice' interface:
#-------------------------------------------------------------------------------

class ITemplateChoice ( Interface ):
    """ Defines the ITemplateChoice interface used by ITemplateDataNameItem
        interface.
    """

    # The user interface string for this choice:
    choice_value = Str

