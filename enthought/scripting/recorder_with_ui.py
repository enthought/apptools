"""
A Recorder subclass that presents a simple user interface.
"""
# Author: Prabhu Ramachandran <prabhu@aero.iitb.ac.in>
# Copyright (c) 2008, Prabhu Ramachandran.
# License: BSD Style.

from enthought.traits.api import Code, Button, Int, on_trait_change
from enthought.traits.ui.api import View, Item, Group, CodeEditor

from recorder import Recorder


################################################################################
# `RecorderWithUI` class.
################################################################################ 
class RecorderWithUI(Recorder):
    """
    This class represents a Recorder but with a simple user interface.
    """

    # The code to display
    code = Code(editor=CodeEditor(line='current_line'))

    # Button to save script to file.
    save_script = Button('Save Script')

    # The current line to show, used by the editor.
    current_line = Int

    view = View(
             Group(
                Group(Item('recording', show_label=True)),
                Group(Item('code', show_label=False)),
                Group(Item('save_script', show_label=False)),
                ),
             width=600, height=400,
             id='enthought.scripting.recorder_with_ui',
             buttons=['OK'], resizable=True
             )

    @on_trait_change('lines[]')
    def _update_code(self):
        self.code = self.get_code()
        self.current_line = len(self.lines) + 1

    def _save_script_fired(self):
        self.ui_save()


