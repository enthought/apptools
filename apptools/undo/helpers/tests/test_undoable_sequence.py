from numpy.testing import assert_allclose

from apptools.undo.helpers.undoable_sequence import UndoableSequence


class Sequence(list):
    """ A do-nothing wrapper around `list` which allow weak references.

    See https://docs.python.org/2/library/weakref.html#module-weakref
    """
    pass


def test_change_item():
    sequence = Sequence([0, 0.1, 0.2, 0.3, 0.4])
    proxy_sequence = UndoableSequence(data=sequence)

    proxy_sequence[2] = 0.25
    assert_allclose(sequence[2], 0.25)

    proxy_sequence.command_stack.undo()
    assert_allclose(sequence[2], 0.2)


def test_insert_item():
    sequence = Sequence([0, 0.1, 0.2])
    proxy_sequence = UndoableSequence(data=sequence)

    proxy_sequence.insert(1, 10)
    assert_allclose(sequence, [0, 10, 0.1, 0.2])

    proxy_sequence.command_stack.undo()
    assert_allclose(sequence, [0, 0.1, 0.2])


def test_remove_item():
    sequence = Sequence([0, 0.1, 0.2])
    proxy_sequence = UndoableSequence(data=sequence)

    proxy_sequence.pop(1)
    assert_allclose(sequence, [0, 0.2])

    proxy_sequence.command_stack.undo()
    assert_allclose(sequence, [0, 0.1, 0.2])
