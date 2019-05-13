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
from pyface.action.api import Action
from traits.api import Unicode

# Local imports.
from apptools.appscripting.package_globals import get_script_manager


class StartRecordingAction(Action):
    """An action that starts the recording of changes to scriptable objects to
    a script."""

    #### 'Action' interface ###################################################

    name = Unicode("Start recording")

    ###########################################################################
    # 'Action' interface.
    ###########################################################################

    def perform(self, event):
        """ Perform the action. """

        get_script_manager().start_recording()
