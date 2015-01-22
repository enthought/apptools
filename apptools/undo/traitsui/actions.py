
# (C) Copyright 2015 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
"""
Traits Actions
==============

This module provides replacements for the standard TraitsUI UndoAction and
RedoAction which update correctly when used with an UndoHandler or subclass
thereof.

"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from traitsui.api import Action

# The standard "undo last change" action:
UndoAction = Action(
    name         = 'Undo',
    action       = '_on_undo',
    enabled_when = 'ui.handler.command_stack.undo_name != ""'
)

# The standard "redo last undo" action:
RedoAction = Action(
    name         = 'Redo',
    action       = '_on_redo',
    enabled_when = 'ui.handler.command_stack.redo_name != ""'
)
