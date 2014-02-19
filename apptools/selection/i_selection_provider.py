from traits.api import Interface, Str


class ISelectionProvider(Interface):

    id = Str()

    def get_selection(self):
        """ """
