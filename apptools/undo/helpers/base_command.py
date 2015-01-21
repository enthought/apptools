from apptools.undo.api import AbstractCommand
from traits.api import Disallow


class BaseCommand(AbstractCommand):

    # Require strict traits definitions.
    _ = Disallow

    def redo(self):
        self.do()
