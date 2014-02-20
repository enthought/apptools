from traits.api import HasTraits, List, provides, Str

from apptools.selection.i_selection import IListSelection


@provides(IListSelection)
class ListSelection(HasTraits):
    """ Selection for ordered sequences of items.

    This is the default implementation of the :class:`~.IListSelection`
    interface.
    """

    #### 'ISelection' protocol ################################################

    #: ID of the selection provider that created this selection object.
    source_id = Str

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
    def from_available_items(cls, source_id, selected, all_items):
        """ Create a list selection given a list of all available items.

        Fills in the required information (in particular, the indices) based
        on a list of selected items and a list of all available items.

        The list of available items must not contain any duplicate items.
        """
        indices = [all_items.index(x) for x in selected]

        return cls(source_id=source_id, items=selected, indices=indices)
