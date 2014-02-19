from traits.api import Interface


class ISelection(Interface):

    def is_empty(self):
        """ Is the selection empty? """
