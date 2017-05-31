"""Simple utility functions provided by the scripting API.
"""
# Author: Prabhu Ramachandran <prabhu [at] aero . iitb . ac . in>
# Copyright (c) 2008,  Prabhu Ramachandran
# License: BSD Style.

from .recorder import Recorder
from .recorder_with_ui import RecorderWithUI
from .package_globals import get_recorder, set_recorder


################################################################################
# Utility functions.
################################################################################
def start_recording(object, ui=True, **kw):
    """Convenience function to start recording.  Returns the recorder.

    Parameters:
    -----------

    object :  object to record.

    ui : bool specifying if a UI is to be shown or not

    kw : Keyword arguments to pass to the register function of the
    recorder.
    """
    if ui:
        r = RecorderWithUI(root=object)
        r.edit_traits(kind='live')
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
