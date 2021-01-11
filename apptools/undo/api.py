# ------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Riverbank Computing Limited
# Description: <Enthought undo package component>
# ------------------------------------------------------------------------------

""" API for apptools.undo subpackage.

- :class:`~.AbstractCommand`
- :class:`~.CommandStack`
- :class:`~.UndoManager`

Interfaces
----------

- :class:`~.ICommand`
- :class:`~.ICommandStack`
- :class:`~.IUndoManager`
"""

from pyface.undo.api import (
    AbstractCommand,
    CommandStack,
    ICommand,
    ICommandStack,
    IUndoManager,
    UndoManager,
)
