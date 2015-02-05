#
# (C) Copyright 2015 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
from __future__ import absolute_import, division, print_function, unicode_literals

# Enthought library imports
from traits.api import HasTraits, Str
from traits.testing.unittest_tools import UnittestTools, unittest

# Local library imports
from apptools.undo.abstract_command import AbstractCommand
from apptools.undo.traitsui.trait_set_command import TraitSetCommand


class DummyHasTraits(HasTraits):

    #: dummy attribute to set
    dummy_trait = Str

    #: dummy attribute with label metadata
    dummy_trait_with_label = Str(label='my name')

    #: dummy non-mergeable trait
    dummy_unmergeable = Str(mergeable=False)


class TestTraitSetCommand(UnittestTools, unittest.TestCase):
    """ Test TraitSetCommand's interface """

    def setUp(self):
        self.data = DummyHasTraits(dummy_trait='initial value')
        self.command = TraitSetCommand(
            mergeable=True,
            data=self.data,
            trait_name='dummy_trait',
            value='new value')

    def test_name_default(self):
        self.assertEqual(self.command.name, 'Change Dummy Trait')

    def test_name_default_with_label(self):
        self.command.trait_name = 'dummy_trait_with_label'
        self.assertEqual(self.command.name, 'Change My Name')

    def test_do(self):
        command = self.command

        with self.assertTraitChanges(self.data, 'dummy_trait', count=1):
            command.do()

        self.assertEqual(self.data.dummy_trait, 'new value')

    def test_undo(self):
        command = self.command
        command.do()

        with self.assertTraitChanges(self.data, 'dummy_trait', count=1):
            command.undo()

        self.assertEqual(self.data.dummy_trait, 'initial value')

    def test_redo(self):
        command = self.command
        command.do()
        command.undo()

        with self.assertTraitChanges(self.data, 'dummy_trait', count=1):
            command.redo()

        self.assertEqual(self.data.dummy_trait, 'new value')

    def test_merge(self):
        command = self.command
        other_command = TraitSetCommand(
            mergeable=True,
            data=self.data,
            trait_name='dummy_trait',
            value='even newer value')

        with self.assertTraitChanges(command, 'value', count=1):
            result = command.merge(other_command)

        self.assertTrue(result)
        self.assertEqual(command.value, 'even newer value')

    def test_merge_bad_trait(self):
        command = self.command
        other_command = TraitSetCommand(
            mergeable=True,
            data=self.data,
            trait_name='dummy_trait_with_label',
            value='even newer value')

        with self.assertTraitDoesNotChange(command, 'value'):
            result = command.merge(other_command)

        self.assertFalse(result)

    def test_merge_bad_data(self):
        command = self.command
        other_command = TraitSetCommand(
            mergeable=True,
            data=DummyHasTraits(),
            trait_name='dummy_trait',
            value='even newer value')

        with self.assertTraitDoesNotChange(command, 'value'):
            result = command.merge(other_command)

        self.assertFalse(result)

    def test_merge_bad_command(self):
        command = self.command
        other_command = AbstractCommand()

        with self.assertTraitDoesNotChange(command, 'value'):
            result = command.merge(other_command)

        self.assertFalse(result)

    def test_merge_not_mergeable(self):
        command = self.command
        command.mergeable = False
        other_command = TraitSetCommand(
            mergeable=True,
            data=self.data,
            trait_name='dummy_trait',
            value='even newer value')

        with self.assertTraitDoesNotChange(command, 'value'):
            result = command.merge(other_command)

        self.assertFalse(result)

    def test_merge_not_mergeable(self):
        command = self.command
        command.trait_name = 'dummy_unmergeable'
        other_command = TraitSetCommand(
            mergeable=True,
            data=self.data,
            trait_name='dummy_unmergeable',
            value='even newer value')

        with self.assertTraitDoesNotChange(command, 'value'):
            result = command.merge(other_command)

        self.assertFalse(result)
