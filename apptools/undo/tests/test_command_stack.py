# -----------------------------------------------------------------------------
#
#  Copyright (c) 2015, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
# -----------------------------------------------------------------------------

from traits.testing.unittest_tools import unittest

from apptools.undo.api import CommandStack, UndoManager
from apptools.undo.tests.testing_commands import SimpleCommand, UnnamedCommand


class TestCommandStack(unittest.TestCase):
    def setUp(self):
        self.stack = CommandStack()
        undo_manager = UndoManager()
        self.stack.undo_manager = undo_manager

        self.command = SimpleCommand()

    # Assertion helpers -------------------------------------------------------

    def assert_n_commands_pushed(self, n):
        # Starting from an empty command stack, N commands have been pushed and
        # then reverted. The stack contains the commands...
        self.assertEqual(len(self.stack._stack), n)
        # ... and the state is at the tip of the stack...
        self.assertEqual(self.stack._index, n-1)
        # ... which is dirty unless nothing was pushed.
        if n > 0:
            self.assertFalse(self.stack.clean)
        else:
            self.assertTrue(self.stack.clean)

    def assert_n_commands_pushed_and_undone(self, n):
        # Starting from an empty command stack, N commands have been pushed and
        # then reverted. The stack still contains the commands...
        self.assertEqual(len(self.stack._stack), n)
        # ... but we are back to the initial (clean) state
        self.assertEqual(self.stack._index, -1)
        self.assertTrue(self.stack.clean)

    # Tests -------------------------------------------------------------------

    def test_empty_command_stack(self):
        self.assert_n_commands_pushed(self, 0)

    def test_1_command_pushed(self):
        self.stack.push(self.command)
        self.assert_n_commands_pushed(1)

    def test_n_command_pushed(self):
        n = 4
        for i in range(n):
            self.stack.push(self.command)

        self.assert_n_commands_pushed(n)

    def test_undo_1_command(self):
        self.stack.push(self.command)

        self.assertEqual(self.stack.undo_name, self.command.name)
        self.stack.undo()

        self.assert_n_commands_pushed_and_undone(1)

    def test_undo_unnamed_command(self):
        unnamed_command = UnnamedCommand()
        self.stack.push(unnamed_command)

        self.assert_n_commands_pushed(1)

        # But the command cannot be undone because it has no name
        self.assertEqual(self.stack.undo_name, "")
        self.stack.undo()

        self.assert_n_commands_pushed(1)

    def test_undo_redo_1_command(self):
        self.stack.push(self.command)
        self.stack.undo()
        self.stack.redo()
        self.assert_n_commands_pushed(1)

    def test_define_macro(self):
        add_macro(self.stack, num_commands=2)
        self.assert_n_commands_pushed(1)

    def test_undo_macro(self):
        add_macro(self.stack, num_commands=2)
        self.stack.undo()
        # The 2 pushes are viewed as 1 command
        self.assert_n_commands_pushed_and_undone(1)

    def test_make_clean(self):
        self.stack.push(self.command)
        self.assertFalse(self.stack.clean)

        self.stack.clean = True
        self.assertTrue(self.stack.clean)

    def test_make_dirty(self):
        self.stack.push(self.command)
        self.stack.clean = True
        self.assertTrue(self.stack.clean)

        self.stack.clean = False
        self.assertFalse(self.stack.clean)


def add_macro(stack, num_commands=2):
    command = SimpleCommand()
    stack.begin_macro('Increment n times')
    try:
        for i in range(num_commands):
            stack.push(command)
    finally:
        stack.end_macro()
