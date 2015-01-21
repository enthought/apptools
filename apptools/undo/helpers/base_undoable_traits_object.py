import logging
from contextlib import contextmanager

from apptools.undo.api import AbstractCommand, ICommandStack
from traits.api import (Any, Dict, HasStrictTraits, Instance, Str, WeakRef,
                        on_trait_change)


log = logging.getLogger(__name__)


class BaseUndoableTraitsObject(HasStrictTraits):
    """ Base class for traits objects that need undo capabilities.

    Simple, recordable traits should be defined with the `record=True` flag.
    This automatically creates a `Command` object and adds it to the undo
    manager. More complex changes should define custom handlers.

    There's no reason to explicitly define a trait with `record=False`, but
    `record` is internally set to `False` during snap-shot operations.
    """

    command_stack = Instance(ICommandStack)

    obj = Any

    _snapshot_start_values = Dict

    @on_trait_change('+record')
    def _add_command_to_stack(self, proxy, name, old, new):
        if proxy.trait(name).record:
            self._execute_and_save_command(name, old, new)
        else:
            self._set_data_value(name, new)

    def start_snapshot(self, attr_name, value):
        """ Start a snapshot command.

        The value at the start of a snapshot is recorded as the "old" value
        of a Command pushed to the undo stack.
        """
        self._set_record_state(attr_name, False)

        self._snapshot_start_values[attr_name] = value
        self._set_data_value(attr_name, value)

    def stop_snapshot(self, attr_name, value):
        """ Stop a snapshot command.

        Save Command to the undo stack and restart the normal recording state.
        """
        old_value = self._pop_snapshot_start_value(attr_name)
        self._execute_and_save_command(attr_name, old_value, value)

        self._set_record_state(attr_name, True)

    def cancel_snapshot(self, attr_name):
        """ Cancel a snapshot command.

        Reset to start value and restart the normal recording state.
        """
        old_value = self._pop_snapshot_start_value(attr_name)
        self._set_data_value(attr_name, old_value)

        self._set_record_state(attr_name, True)

    def _pop_snapshot_start_value(self, attr_name):
        if attr_name not in self._snapshot_start_values:
            msg = "Attempted to retrieve unknown snapshot value for {!r}"
            log.warn(msg.format(attr_name))
        return self._snapshot_start_values.pop(attr_name)

    def _set_record_state(self, attr_name, new_state):
        attribute = self.trait(attr_name)
        assert attribute.record == (not new_state)
        attribute.record = new_state

    def _set_data_value(self, attr_name, value):
        setattr(self.obj, attr_name, value)

    def _execute_and_save_command(self, attr_name, old_value, new_value):
        """ Create, execute, and save an attribute-change command. """
        name = self.trait(attr_name).action_name
        if not name:
            raise RuntimeError("Recorded traits must define `action_name`.")

        data = AttrChangeData(proxy=self, attr_name=attr_name,
                              old_value=old_value, new_value=new_value)
        command = AttrChangeCommand(name=name, data=data)
        self.command_stack.push(command)


class AttrChangeData(HasStrictTraits):

    #: Parent object of the altered attribute.
    proxy = WeakRef(HasStrictTraits)

    #: Name of the altered attribute.
    attr_name = Str

    #: The value of the attribute before the change.
    old_value = Any

    #: The value of the attribute after the change.
    new_value = Any


class AttrChangeCommand(AbstractCommand):
    """ Command which changes an attribute on an object.
    """

    #: Object that controls
    data = Instance(AttrChangeData)

    def _name_default(self):
        return '{!r} changed'.format(self.data.attr_name)

    def do(self):
        setattr(self.data.proxy, self.data.attr_name, self.data.new_value)

    def redo(self):
        self.do()

    def undo(self):
        if self.data.proxy is None:
            log.warn("Attempted Undo {!r} on deleted object".format(self.name))
            return

        # Note that changes to real object would fire changes on undoable
        # but we don't want to add this action to the undo stack.
        with record_loopback_guard(self.data.proxy, self.data.attr_name):
            setattr(self.data.proxy, self.data.attr_name, self.data.old_value)


@contextmanager
def record_loopback_guard(proxy, attr_name):
    """ Context where a trait's `record` metadata is temporarily set to False.
    """
    # This shouldn't happen, right?
    assert proxy.trait(attr_name).record

    proxy.trait(attr_name).record = False
    yield
    proxy.trait(attr_name).record = True
