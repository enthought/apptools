#
# (C) Copyright 2015 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
from __future__ import absolute_import, division, print_function, unicode_literals

# Enthought library imports
from traits.api import Event, HasTraits, Property, Str, TraitError
from traits.testing.unittest_tools import UnittestTools, unittest

# Local library imports
from apptools.undo.command_stack import CommandStack
from apptools.undo.undo_manager import UndoManager
from apptools.undo.traitsui.trait_set_command import TraitSetCommand
from apptools.undo.traitsui.undo_handler import UndoHandler


class DummyHasTraits(HasTraits):

    #: dummy attribute to set
    dummy_trait = Str

    #: dummy event to set
    dummy_event = Event

    #: regular property
    dummy_property = Property

    #: write-only property
    dummy_write_only = Property

    def _get_dummy_property(self):
        return self.dummy_trait

    def _set_dummy_property(self, value):
        self.dummy_trait = value

    def _set_dummy_write_only(self, value):
        self.dummy_trait = value


class TestUndoHandler(UnittestTools, unittest.TestCase):
    """ Test UndoHandler's interface """

    def setUp(self):
        self.command_stack = CommandStack(undo_manager=UndoManager())
        self.handler = UndoHandler(command_stack=self.command_stack)
        self.object = DummyHasTraits(dummy_trait='old value')

    def test_setattr(self):
        info = None

        with self.assertTraitChanges(self.object, 'dummy_trait', count=1), \
                self.assertTraitChanges(self.command_stack, '_stack_items'):
            self.handler.setattr(info, self.object, 'dummy_trait', 'new value')

        self.assertEquals(self.object.dummy_trait, 'new value')
        self.assertEquals(len(self.command_stack._stack), 1)

        command = self.command_stack._stack[0].command
        self.assertIsInstance(command, TraitSetCommand)
        self.assertEquals(command.data, self.object)
        self.assertEquals(command.trait_name, 'dummy_trait')
        self.assertEquals(command.value, 'new value')

    def test_setattr_event(self):
        info = None

        with self.assertTraitChanges(self.object, 'dummy_event', count=1), \
                self.assertTraitDoesNotChange(self.command_stack, '_stack_items'):
            self.handler.setattr(info, self.object, 'dummy_event', 'new value')

        self.assertEquals(len(self.command_stack._stack), 0)

    def test_setattr_property(self):
        info = None

        with self.assertTraitChanges(self.object, 'dummy_trait', count=1), \
                self.assertTraitChanges(self.command_stack, '_stack_items'):
            self.handler.setattr(info, self.object, 'dummy_property', 'new value')

        self.assertEquals(len(self.command_stack._stack), 1)

        command = self.command_stack._stack[0].command
        self.assertIsInstance(command, TraitSetCommand)
        self.assertEquals(command.data, self.object)
        self.assertEquals(command.trait_name, 'dummy_property')
        self.assertEquals(command.value, 'new value')

    def test_setattr_write_only(self):
        info = None

        with self.assertTraitDoesNotChange(self.command_stack, '_stack_items'):
            self.handler.setattr(info, self.object, 'dummy_write_only', 'new value')

        self.assertEquals(self.object.dummy_trait, 'new value')
        self.assertEquals(len(self.command_stack._stack), 0)

    def test_setattr_bad(self):
        info = None

        with self.assertTraitDoesNotChange(self.object, 'dummy_trait', count=1), \
                self.assertTraitDoesNotChange(self.command_stack, '_stack_items'):
            with self.assertRaises(TraitError):
                self.handler.setattr(info, self.object, 'dummy_trait', 1)

        self.assertEquals(len(self.command_stack._stack), 0)

    def test_on_undo(self):
        info = None
        self.handler.setattr(info, self.object, 'dummy_trait', 'new value')

        with self.assertTraitChanges(self.object, 'dummy_trait', count=1):
            self.handler._on_undo(info)

        self.assertEquals(self.object.dummy_trait, 'old value')

    def test_on_redo(self):
        info = None
        self.handler.setattr(info, self.object, 'dummy_trait', 'new value')
        self.handler._on_undo(info)

        with self.assertTraitChanges(self.object, 'dummy_trait', count=1):
            self.handler._on_redo(info)

        self.assertEquals(self.object.dummy_trait, 'new value')
