#
# (C) Copyright 2015 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
"""
UndoHandler
===========

This module provides a simple replacement for the standard TraitsUI ``Handler``
which instead of setting values via ``setattr`` it creates a
``TraitSetCommand`` that records the old value and sets the new one.

This has the net effect of allowing a regular TraitsUI view to be converted
into one for which simple editors will now generate undoable commands.

The primary use case is for panel-style UIs embedded within a Tasks application
(or something similar), and so we don't currently try to do something sensible
with the ``apply`` and ``revert`` methods.

"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Enthought library imports
from traits.api import Instance, TraitError
from traitsui.api import Handler

# Local library imports
from apptools.undo.i_command_stack import ICommandStack
from .trait_set_command import TraitSetCommand


class UndoHandler(Handler):
    """ Handler that sets attributes via Commands

    This permits easy conversion of TraitsUI to participate in apptools.undo
    undo/redo behaviour.  Insted of calling Python's standard ``setattr`` it
    creates a ``TraitSetCommand`` that records the old value and sets the new
    one.

    The handler needs to be supplied with a command stack on which it will
    operate.

    """

    #-------------------------------------------------------------------------
    # 'UndoHandler' interface
    #-------------------------------------------------------------------------

    #: The command stack that this handler uses.
    command_stack = Instance(ICommandStack)

    #-------------------------------------------------------------------------
    # 'Handler' interface
    #-------------------------------------------------------------------------

    def setattr(self, info, object, name, value):
        """ Create an undoable command that sets the appropriate trait """
        # special-case events (and buttons, in particular)
        if object.trait(name).type == 'event':
            super(UndoHandler, self).setattr(info, object, name, value)
            return

        command = TraitSetCommand(data=object, trait_name=name, value=value)

        try:
            self.command_stack.push(command)
        except TraitError:
            # the most likely cause is a write-only property, try normal set
            super(UndoHandler, self).setattr(info, object, name, value)

    # 'Handler' private methods

    def _on_undo(self, info):
        if self.command_stack is not None:
            self.command_stack.undo()

    def _on_redo(self, info):
        if self.command_stack is not None:
            self.command_stack.redo()
