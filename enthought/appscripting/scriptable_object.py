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


# Enthought library imports.
from enthought.traits.api import HasTraits, Instance

# Local imports.
from script_manager import ScriptManager


class ScriptableObject(HasTraits):
    """ The ScriptableObject class is the base class for any class that has
    scriptable traits or methods.
    """

    #### 'ScriptableObject' interface ########################################

    # This is the script manager that manages this object.
    script_manager = Instance(ScriptManager)

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, *args, **kwargs):
        """ Initialise the instance. """

        super(ScriptableObject, self).__init__(*args, **kwargs)

        # Register the object in case __init__ wasn't decorated.
        self.script_manager.new_object(self, args, kwargs)
