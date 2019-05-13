#-------------------------------------------------------------------------------
#
#  A concrete implementation of the ITemplateChoice interface that can be used
#  as is for simple cases, or extended for more complex ones.
#
#  Written by: David C. Morrill
#
#  Date: 07/29/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import HasPrivateTraits, Str, provides

from .itemplate_choice \
    import ITemplateChoice

#-------------------------------------------------------------------------------
#  'TemplateChoice' class:
#-------------------------------------------------------------------------------

class TemplateChoice ( HasPrivateTraits ):

    implements ( ITemplateChoice )

    # The user interface string for this choice:
    choice_value = Str

