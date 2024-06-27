# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
from traits.api import HasTraits, List, provides, Str

from apptools.selection.i_selection import IListSelection


@provides(IListSelection)
class ListSelection(HasTraits):
    """Selection for ordered sequences of items.

    This is the default implementation of the :class:`~.IListSelection`
    interface.
    """

    #### 'ISelection' protocol ################################################

    #: ID of the selection provider that created this selection object.
    provider_id = Str

    def is_empty(self):
        """ Is the selection empty? """
        return len(self.items) == 0

    #### 'IListSelection' protocol ############################################

    #: Selected objects.
    items = List

    #: Indices of the selected objects in the selection provider.
    indices = List

    #### 'ListSelection' class protocol #######################################

    @classmethod
    def from_available_items(cls, provider_id, selected, all_items):
        """Create a list selection given a list of all available items.

        Fills in the required information (in particular, the indices) based
        on a list of selected items and a list of all available items.

        .. note::
            - The list of available items must not contain any duplicate items.
            - It is expected that ``selected`` is populated by items in
              ``all_items``.

        """
        number_of_items = len(all_items)
        indices = []

        for item in selected:
            for index in range(number_of_items):
                if all_items[index] is item:
                    indices.append(index)
                    break
            else:
                msg = "Selected item: {!r}, could not be found"
                raise ValueError(msg.format(item))

        return cls(provider_id=provider_id, items=selected, indices=indices)
