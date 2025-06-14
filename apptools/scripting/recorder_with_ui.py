# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
"""
A Recorder subclass that presents a simple user interface.
"""

from traits.api import Code, Button, Int, observe, Any
from traitsui.api import View, Item, Group, HGroup, CodeEditor, spring, Handler

from .recorder import Recorder


###############################################################################
# `CloseHandler` class.
###############################################################################
class CloseHandler(Handler):
    """This class cleans up after the UI for the recorder is closed."""

    def close(self, info, is_ok):
        """This method is invoked when the user closes the UI."""
        recorder = info.object
        recorder.on_ui_close()
        return True


###############################################################################
# `RecorderWithUI` class.
###############################################################################
class RecorderWithUI(Recorder):
    """
    This class represents a Recorder but with a simple user interface.
    """

    # The code to display
    code = Code(editor=CodeEditor(line="current_line"))

    # Button to save script to file.
    save_script = Button("Save Script")

    # The current line to show, used by the editor.
    current_line = Int

    # The root object which is being recorded.
    root = Any

    ########################################
    # Traits View.
    view = View(
        Group(
            HGroup(
                Item("recording", show_label=True),
                spring,
                Item("save_script", show_label=False),
            ),
            Group(Item("code", show_label=False)),
        ),
        width=600,
        height=360,
        id="apptools.scripting.recorder_with_ui",
        buttons=["Cancel"],
        resizable=True,
        handler=CloseHandler(),
    )

    ######################################################################
    # RecorderWithUI interface.
    ######################################################################
    def on_ui_close(self):
        """Called from the CloseHandler when the UI is closed. This
        method basically stops the recording.
        """
        from .util import stop_recording
        from .package_globals import get_recorder

        if get_recorder() is self:
            stop_recording(self.root, save=False)
        else:
            self.recording = False
            self.unregister(self.root)

    ######################################################################
    # Non-public interface.
    ######################################################################
    @observe("lines.items")
    def _update_code(self, event):
        self.code = self.get_code()
        self.current_line = len(self.lines) + 1

    def _save_script_fired(self):
        self.ui_save()
