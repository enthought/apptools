from traits.api import Interface, Str


class ISelection(Interface):
    """ Collection of selected items. """

    #: ID of the selection provider that created this selection object.
    source_id = Str

    def is_empty(self):
        """ Is the selection empty? """
