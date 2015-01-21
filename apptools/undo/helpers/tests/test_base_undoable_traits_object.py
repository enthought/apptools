import gc

import numpy as np
from numpy.testing import assert_allclose, assert_equal

from apptools.undo.api import UndoManager, CommandStack
from apptools.undo.helpers.base_undoable_traits_object import \
    BaseUndoableTraitsObject
from traits.api import DelegatesTo, Float, HasStrictTraits, Instance, Int, Str



class ObjectData(HasStrictTraits):

    a_float = Float(0)

    an_int = Int(0)

    a_str = Str('')


class UndoableObject(BaseUndoableTraitsObject):

    obj = Instance(ObjectData, ())

    a_float = DelegatesTo('obj', record=True, action_name='Set float')

    an_int = DelegatesTo('obj', record=True, action_name='Set int')

    a_str = DelegatesTo('obj', record=True, action_name='Set string')

    def _command_stack_default(self):
        return CommandStack(undo_manager=UndoManager())


def test_add_to_stack():
    # Test that changing an attribute on the object changes its
    # corresponding value on the data model and pushes an undo entry.
    proxy = UndoableObject()
    data = proxy.obj

    proxy.a_float = 1.1
    assert_allclose(data.a_float, 1.1)
    assert proxy.command_stack.undo_name == 'Set float'

    proxy.an_int = 42
    assert data.an_int == 42
    assert proxy.command_stack.undo_name == 'Set int'

    proxy.a_str = 'Hi'
    assert data.a_str == 'Hi'
    assert proxy.command_stack.undo_name == 'Set string'


def test_undo_sequence():
    proxy = UndoableObject()
    real_obj = proxy.obj

    # Set `an_int` with values 1 through 4 (initially `an_int = 0`)
    values = range(5)
    for i in values[1:]:
        proxy.an_int = i

    # Assert that a sequence of undo operations returns 3 through 0.
    for expected_int in values[-2::-1]:
        proxy.command_stack.undo()
        assert_equal(proxy.an_int, expected_int)
        assert_equal(real_obj.an_int, expected_int)


def test_deleted_object():
    # Make sure the undo stack only has a weak reference to proxy object and
    # that calling undo on a deleted object logs a warning.
    proxy = UndoableObject()
    real_obj = proxy.obj

    # Edit the data so we have a reference to `proxy` on the command stack.
    proxy.an_int = 42

    assert len(gc.get_referrers(real_obj)) > 1
    del proxy
    # Only the reference in this test exists now.
    assert len(gc.get_referrers(real_obj)) == 1


def test_undo_redo():
    proxy = UndoableObject()
    real_obj = proxy.obj

    proxy.an_int = 10
    proxy.an_int = 100

    proxy.command_stack.undo()
    assert_equal(real_obj.an_int, 10)

    proxy.command_stack.redo()
    assert_equal(real_obj.an_int, 100)

    # One last `undo` to make sure that `redo` pushes to the undo stack.
    proxy.command_stack.undo()
    assert_equal(real_obj.an_int, 10)


def test_snapshot():
    proxy = UndoableObject()
    real_obj = proxy.obj

    # Start snapshot at some "old" value.
    proxy.start_snapshot('a_float', 1)
    assert_allclose(real_obj.a_float, 1)

    # Changes during a snapshot change the data model.
    for value in np.linspace(2, 3, 10):
        proxy.a_float = value
        assert_allclose(real_obj.a_float, value)

    # Stop snapshot to save to the command stack.
    proxy.stop_snapshot('a_float', 4)
    assert_allclose(real_obj.a_float, 4)

    # Undo return to value at the start of the snapshot.
    proxy.command_stack.undo()
    assert_allclose(real_obj.a_float, 1)


def test_cancel_snapshot():
    proxy = UndoableObject()
    real_obj = proxy.obj

    # Start snapshot at some "old" value.
    proxy.start_snapshot('a_float', 1)
    assert_allclose(real_obj.a_float, 1)

    proxy.a_float = 10
    assert_allclose(real_obj.a_float, 10)

    # Cancel snapshot and make sure we return to the start value
    proxy.cancel_snapshot('a_float')
    assert_allclose(real_obj.a_float, 1)
