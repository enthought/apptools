#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------

from unittest import TestCase

from apptools.undo.api import CommandStack, UndoManager
from testing_commands import SimpleCommand, UnnamedCommand


class TestCommandStack(TestCase):
    def setUp(self):
        self.stack = CommandStack()
        undo_manager = UndoManager()
        self.stack.undo_manager = undo_manager

        self.command = SimpleCommand()

    def test_empty_command_stack(self):
        self.assertEqual(self.stack._stack, [])
        self.assertEqual(self.stack._index, -1)
        self.assertTrue(self.stack.clean)

    def test_1_command_pushed(self):
        self.stack.push(self.command)

        # Everything has been shifted forward
        self.assertEqual(len(self.stack._stack), 1)
        self.assertEqual(self.stack._index, 0)
        self.assertFalse(self.stack.clean)

    def test_n_command_pushed(self):
        n = 4
        for i in range(n):
            self.stack.push(self.command)

        # Everything has been shifted forward by n commands
        self.assertEqual(len(self.stack._stack), n)
        self.assertEqual(self.stack._index, n-1)
        self.assertFalse(self.stack.clean)

    def test_undo_1_command(self):
        self.stack.push(self.command)

        self.assertEqual(self.stack.undo_name, self.command.name)
        self.stack.undo()

        # The stack still contains the command but the index is back to start
        self.assertEqual(len(self.stack._stack), 1)
        self.assertEqual(self.stack._index, -1)
        self.assertTrue(self.stack.clean)

    def test_undo_unnamed_command(self):
        unnamed_command = UnnamedCommand()
        self.stack.push(unnamed_command)

        # Everything has been shifted forward
        self.assertEqual(len(self.stack._stack), 1)
        self.assertEqual(self.stack._index, 0)
        self.assertFalse(self.stack.clean)

        # But the command cannot be undone because it has no name
        self.assertEqual(self.stack.undo_name, "")
        self.stack.undo()

        self.assertEqual(len(self.stack._stack), 1)
        self.assertEqual(self.stack._index, 0)
        self.assertFalse(self.stack.clean)

    def test_undo_redo_1_command(self):
        self.stack.push(self.command)
        self.stack.undo()
        self.stack.redo()

        # Everything has been shifted forward by 1 command
        self.assertEqual(len(self.stack._stack), 1)
        self.assertEqual(self.stack._index, 0)
        self.assertFalse(self.stack.clean)


    def test_define_macro(self):
        self.stack.begin_macro('Increment twice')
        try:
            self.stack.push(self.command)
            self.stack.push(self.command)
        finally:
            self.stack.end_macro()

        # The 2 pushes are viewed as 1 command
        self.assertEqual(len(self.stack._stack), 1)
        self.assertEqual(self.stack._index, 0)
        self.assertFalse(self.stack.clean)

    def test_undo_macro(self):
        self.stack.begin_macro('Increment twice')
        try:
            self.stack.push(self.command)
            self.stack.push(self.command)
        finally:
            self.stack.end_macro()

        self.stack.undo()

        # The 2 pushes are viewed as 1 command
        self.assertEqual(len(self.stack._stack), 1)
        self.assertEqual(self.stack._index, -1)
        self.assertTrue(self.stack.clean)
