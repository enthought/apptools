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
from enthought.pyface.action.api import Action, Group, MenuManager
from enthought.pyface.workbench.api import WorkbenchWindow
from enthought.pyface.workbench.action.api import MenuBarManager, \
        ToolBarManager
from enthought.traits.api import Instance, on_trait_change
from enthought.appscripting.api import get_script_manager
from enthought.appscripting.action.api import StartRecordingAction, \
        StopRecordingAction

# Local imports.
from example_editor_manager import ExampleEditorManager
from actions import LabelIncrementSizeAction, LabelDecrementSizeAction, \
        LabelNormalFontAction, LabelBoldFontAction, LabelItalicFontAction


class ExampleScriptWindow(WorkbenchWindow):
    """ The ExampleScriptWindow class is a workbench window that contains
    example editors that demonstrate the use of the application scripting
    framework.
    """

    #### Private interface ####################################################

    # The action that exits the application.
    _exit_action = Instance(Action)

    # The File menu.
    _file_menu = Instance(MenuManager)

    # The Label menu.
    _label_menu = Instance(MenuManager)

    # The Scripts menu.
    _scripts_menu = Instance(MenuManager)

    ###########################################################################
    # Private interface.
    ###########################################################################

    #### Trait initialisers ###################################################

    def __file_menu_default(self):
        """ Trait initialiser. """

        return MenuManager(self._exit_action, name="&File")

    def __label_menu_default(self):
        """ Trait initialiser. """

        size_group = Group(LabelIncrementSizeAction(window=self),
                LabelDecrementSizeAction(window=self))

        normal = LabelNormalFontAction(window=self, id='normal', style='radio',
                checked=True)
        bold = LabelBoldFontAction(window=self, id='bold', style='radio')
        italic = LabelItalicFontAction(window=self, id='italic', style='radio')

        style_group = Group(normal, bold, italic, id='style')

        return MenuManager(size_group, style_group, name="&Label")

    def __scripts_menu_default(self):
        """ Trait initialiser. """

        # ZZZ: This is temporary until we put the script into a view.
        get_script_manager().on_trait_event(self._on_script_updated,
                'script_updated')

        return MenuManager(StartRecordingAction(), StopRecordingAction(),
                name="&Scripts")

    def __exit_action_default(self):
        """ Trait initialiser. """

        return Action(name="E&xit", on_perform=self.workbench.exit)

    def _editor_manager_default(self):
        """ Trait initialiser. """

        return ExampleEditorManager()

    def _menu_bar_manager_default(self):
        """ Trait initialiser. """

        return MenuBarManager(self._file_menu, self._label_menu,
                self._scripts_menu, window=self)

    def _tool_bar_manager_default(self):
        """ Trait initialiser. """

        return ToolBarManager(self._exit_action, show_tool_names=False)

    # ZZZ: This is temporary until we put the script into a view.
    def _on_script_updated(self, script_manager):
        script = script_manager.script

        if script:
            print script,
        else:
            print "Script empty"

#### EOF ######################################################################
