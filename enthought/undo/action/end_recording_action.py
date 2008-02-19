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
from enthought.traits.api import Bool, Unicode

# Local imports.
from abstract_undo_action import AbstractUndoAction


class EndRecordingAction(AbstractUndoAction):
    """ An action that ends the recording of changes to scriptable objects to a
    script. """

    #### 'Action' interface ###################################################

    enabled = Bool(False)

    name = Unicode("End recording")

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **traits):
        """ Initialise the instance. """

        super(EndRecordingAction, self).__init__(**traits)

        self.undo_manager.on_trait_change(self._on_recording, 'recording')

    ###########################################################################
    # 'Action' interface.
    ###########################################################################

    def perform(self, event):
        """ Perform the action. """

        self.undo_manager.end_recording()

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _on_recording(self, new):
        """ Handle a change to the undo manager's recording trait. """

        self.enabled = new
