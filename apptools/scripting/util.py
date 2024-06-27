# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
"""Simple utility functions provided by the scripting API.
"""

from .recorder import Recorder
from .recorder_with_ui import RecorderWithUI
from .package_globals import get_recorder, set_recorder


###############################################################################
# Utility functions.
###############################################################################
def start_recording(object, ui=True, **kw):
    """Convenience function to start recording.  Returns the recorder.

    Parameters
    ----------

    object :  object to record.

    ui : bool specifying if a UI is to be shown or not

    kw : Keyword arguments to pass to the register function of the
    recorder.
    """
    if ui:
        r = RecorderWithUI(root=object)
        r.edit_traits(kind="live")
    else:
        r = Recorder()
    # Set the global recorder.
    set_recorder(r)
    r.recording = True
    r.register(object, **kw)
    return r


def stop_recording(object, save=True):
    """Stop recording the object.  If `save` is `True`, this will pop up
    a UI to ask where to save the script.
    """
    recorder = get_recorder()
    recorder.unregister(object)
    recorder.recording = False
    # Set the global recorder back to None
    set_recorder(None)
    # Save the script.
    if save:
        recorder.ui_save()
