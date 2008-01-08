#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
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
#------------------------------------------------------------------------------


# Enthought library imports.
from enthought.traits.api import HasTraits, Instance

# Local imports.
from i_undo_manager import IUndoManager
from script_manager import ScriptManager


class ScriptableObject(HasTraits):
    """ The ScriptableObject class is the base class for any class that has
    scriptable traits or methods.
    """

    #### 'ScriptableObject' interface ########################################

    # This is the undo manager that manages this object.
    undo_manager = Instance(IUndoManager)

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, *args, **kwargs):
        """ Initialise the instance. """

        super(ScriptableObject, self).__init__(*args, **kwargs)

        # Register the object in case __init__ wasn't decorated.
        ScriptManager.new_object(self, args, kwargs)
