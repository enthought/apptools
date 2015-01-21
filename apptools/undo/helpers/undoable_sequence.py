from collections import MutableSequence

from apptools.undo.api import CommandStack, ICommandStack, UndoManager
from traits.api import Any, HasStrictTraits, Instance, Int, Str, WeakRef

from .base_command import BaseCommand


class SetItemData(HasStrictTraits):

    sequence = WeakRef(MutableSequence)
    index = Int
    old_value = Any
    new_value = Any


class ItemValueData(HasStrictTraits):

    sequence = WeakRef(MutableSequence)
    index = Int
    value = Any


class UndoableSequence(HasStrictTraits):
    """ A proxy sequence which adds undo capabilities.

    Although a simple list should work as the `data` proxied by this object,
    we're using weakrefs to the sequence so a simple list will not work.
    See [1]_ for details.

    .. [1] https://docs.python.org/2/library/weakref.html#module-weakref

    """

    #: Command stack used for recording changes.
    command_stack = Instance(ICommandStack)

    #: List data that is being manipulated by the tool.
    data = Instance(MutableSequence)

    #: Name of set-item command.
    name_set_command = Str('Change item')

    #: Name of insert command.
    name_insert_command = Str('Insert item')

    #: Name of remove (`pop`) command.
    name_remove_command = Str('Remove item')

    # -------------------------------------------------------------------------
    #  Public interface
    # -------------------------------------------------------------------------

    def insert(self, index, value):
        data = ItemValueData(sequence=self.data, index=index, value=value)
        command = InsertItemCommand(name=self.name_insert_command, data=data)
        self._execute_and_add_command(command)

    def pop(self, index):
        value = self.data[index]
        data = ItemValueData(sequence=self.data, index=index, value=value)
        command = RemoveItemCommand(name=self.name_remove_command, data=data)
        self._execute_and_add_command(command)

    def __setitem__(self, index, value):
        old_value = self.data[index]
        data = SetItemData(sequence=self.data, index=index,
                           old_value=old_value, new_value=value)
        command = SetItemCommand(name=self.name_set_command, data=data)
        self._execute_and_add_command(command)

    def __iter__(self):
        return self.data.__iter__()

    def __getitem__(self, index):
        return self.data[index]

    def __contains__(self, value):
        return value in self.data

    def __len__(self):
        return len(self.data)

    # -------------------------------------------------------------------------
    #  Private interface
    # -------------------------------------------------------------------------

    def _execute_and_add_command(self, command):
        self.command_stack.push(command)

    def _command_stack_default(self):
        manager = UndoManager()
        return CommandStack(undo_manager=manager)


class SetItemCommand(BaseCommand):
    """ Command which changes an item in a list or sequence. """

    data = Instance(SetItemData)

    def do(self):
        self.data.sequence[self.data.index] = self.data.new_value

    def undo(self):
        self.data.sequence[self.data.index] = self.data.old_value


class InsertItemCommand(BaseCommand):

    data = Instance(ItemValueData)

    #: The value of the item inserted into the sequence.
    value = Any

    def do(self):
        self.data.sequence.insert(self.data.index, self.data.value)

    def undo(self):
        self.data.sequence.pop(self.data.index)


class RemoveItemCommand(InsertItemCommand):

    def do(self):
        super(RemoveItemCommand, self).undo()

    def undo(self):
        super(RemoveItemCommand, self).do()
