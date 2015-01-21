#
# (C) Copyright 2015 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
"""
TraitSetCommand
===============

This module provides a simple command which sets a trait value on ``do`` and
``redo``, resets it to the previous value on ``undo``, and merges multiple
commands on the same attribute on the same object.

"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Enthought library imports
from traits.api import Any, Str

# Local library imports
from apptools.undo.api import AbstractCommand


class TraitSetCommand(AbstractCommand):
    """ Command subclass which simply sets a trait on an object

    This is somewhat simplistic: it assumes that nothing else is going to
    hold on to and mutate the old value unexpectedly, which may break down
    with things like NumPy arrays.  The main purposes is to generate commands
    from the UndoHandler, so we can be reasonably comfortable that the values
    are being handled sanely.

    """

    #-------------------------------------------------------------------------
    # 'TraitSetCommand' interface
    #-------------------------------------------------------------------------

    #: The name of the data trait we are acting on.
    trait_name = Str

    #: The new value that the trait is being set to
    value = Any

    #: The old value of the trait
    _old_value = Any

    #-------------------------------------------------------------------------
    # 'ICommand' interface
    #-------------------------------------------------------------------------

    #: The user-visible name of the command
    name = Str

    def do(self):
        # we assume that copy or deep copy isn't required
        self._old_value = getattr(self.data, self.trait_name)
        self.redo()

    def redo(self):
        setattr(self.data, self.trait_name, self.value)

    def undo(self):
        setattr(self.data, self.trait_name, self._old_value)

    def merge(self, other):
        if (isinstance(other, self.__class__) and self.data is other.data and
                self.trait_name == other.trait_name):
            self.value = other.value
            return True
        return super(TraitSetCommand, self).merge(other)

    # Traits default handlers

    def _name_default(self):
        label = self.data.trait(self.trait_name).label
        if not label:
            label = self.trait_name.replace('_', ' ')
        return "Change "+label.title()
