from traits.api import Interface


class ISelection(Interface):
    """ Collection of selected items. """

    def is_empty(self):
        """ Is the selection empty? """
