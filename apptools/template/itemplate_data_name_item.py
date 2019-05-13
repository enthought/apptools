#-------------------------------------------------------------------------------
#
#  Defines the ITemplateDataNameItem interface used by elements of a
#  TemplateDataName.
#
#  Written by: David C. Morrill
#
#  Date: 07/27/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines the ITemplateDataNameItem interface used by elements of a
    TemplateDataName.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import Interface, Instance, List

from .itemplate_data_context \
    import ITemplateDataContext

from .itemplate_choice \
    import ITemplateChoice

#-------------------------------------------------------------------------------
#  'ITemplateDataNameItem' interface:
#-------------------------------------------------------------------------------

class ITemplateDataNameItem ( Interface ):
    """ Defines the ITemplateDataNameItem interface used by elements of a
        TemplateDataName.

        The contents of the *input_data_context* and *output_data_context*
        are assumed to be immutable. That is, no changes should occur to the
        data contexts once they have been assigned to the
        **ITemplateDataNameItem** traits.

        However, new input contexts can be assigned, in which case a new
        output context should be created and assigned to the output context
        (once it has been fully populated).

        Also, the *output_data_context* should be **None** if the
        *input_data_context* value is **None** or the object cannot match any
        values in the *input_data_context*.
    """

    # The data context which this data name item should match against. This
    # value must be read/write.
    input_data_context = Instance( ITemplateDataContext )

    # The data context containing the data values and/or contexts this data
    # name item matches. This value must be read/write.
    output_data_context = Instance( ITemplateDataContext )

    # The ITemplateChoice instance representing the current settings of the
    # data name item. This value must be read/write.
    data_name_item_choice = Instance( ITemplateChoice )

    # The alternative choices the user has for the data name item settings for
    # the current input data context. The list may be empty, in which case the
    # user cannot change the settings of the data name item. This value can be
    # read only.
    data_name_item_choices = List( ITemplateChoice )


