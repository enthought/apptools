from traits.api import HasTraits, List, provides, Str

from apptools.selection.i_selection import IListSelection


@provides(IListSelection)
class ListSelection(HasTraits):
    """ Selection for ordered sequences of items.

    This is a default implementation if the :class:`~.IListSelection`
    interface, which fills in the required information based on a list of
    selected items and a list of all available items.
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

    #### 'ListSelection' protocol #############################################

    def __init__(self, source_id, selected, all_items):
        indices = [all_items.index(x) for x in selected]

        super(ListSelection, self).__init__(source_id=source_id,
                                            items=selected,
                                            indices=indices)
