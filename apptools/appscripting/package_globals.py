#------------------------------------------------------------------------------
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
# Description: <Enthought application scripting package component>
#------------------------------------------------------------------------------


# The script manager.
_script_manager = None


def get_script_manager():
    """Return the IScriptManager implementation, creating a ScriptManager
    instance if no other implementation has been set."""

    global _script_manager

    if _script_manager is None:
        from .script_manager import ScriptManager

        _script_manager = ScriptManager()

    return _script_manager


def set_script_manager(script_manager):
    """Set the IScriptManager implementation to use."""

    global _script_manager

    _script_manager = script_manager
