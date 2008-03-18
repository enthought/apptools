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
from enthought.traits.api import Bool, Event, Instance, Interface, Unicode

# Local imports.
from i_bind_event import IBindEvent


class IScriptManager(Interface):
    """ The script manager interface.  A script manager is responsible for the
    recording of appropriately annotated user actions as scripts that can be
    executed without user intervention at a later time.  Typically an
    application would have a single script manager.
    """

    #### 'IScriptManager' interface ###########################################

    # This event is fired whenever a scriptable object is bound or unbound.  It
    # is intended to be used by an interactive Python shell to give the
    # advanced user access to the scriptable objects.
    bind_event = Event(IBindEvent)

    # This is set if user actions are being recorded as a script.  It is
    # maintained by the script manager.
    recording = Bool(False)

    # This is the text of the script currently being recorded (or the last
    # recorded script if none is currently being recorded).  It is updated
    # automatically as the user performs actions.
    script = Unicode

    # This event is fired when the recorded script changes.  The value of the
    # event will be the ScriptManager instance.
    script_updated = Event(Instance('enthought.appscripting.api.IScriptManager'))

    ###########################################################################
    # 'IScriptManager' interface.
    ###########################################################################

    def start_recording(self):
        """ Start the recording of user actions.  The 'script' trait is cleared
        and all subsequent actions are added to 'script'.  The 'recording'
        trait is updated appropriately.
        """

    def stop_recording(self):
        """ Stop the recording of user actions.  The 'recording' trait is
        updated appropriately.
        """
