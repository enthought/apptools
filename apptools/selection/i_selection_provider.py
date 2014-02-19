from traits.api import Interface, Str


class ISelectionProvider(Interface):
    """ Source of selections. """

    #: Unique ID identifying the provider.
    id = Str()

    def get_selection(self):
        """ Return the current selection.

        Returns
        -------
        selection -- ISelection
            Object representing the current selection.
        """
