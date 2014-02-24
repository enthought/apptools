from traits.api import Interface, List, Str


class ISelection(Interface):
    """ Collection of selected items. """

    #: ID of the selection provider that created this selection object.
    provider_id = Str

    def is_empty(self):
        """ Is the selection empty? """


class IListSelection(ISelection):
    """ Selection for ordered sequences of items. """

    #: Selected objects.
    items = List

    #: Indices of the selected objects in the selection provider.
    indices = List
