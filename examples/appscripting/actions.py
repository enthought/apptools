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
from enthought.traits.api import Any, Instance, Str, Unicode
from enthought.pyface.action.api import Action
from enthought.pyface.workbench.api import WorkbenchWindow

# Local imports.
from model import Label


class BoundAction(Action):
    """An action with a bound object.  The action is automatically disabled if
    the bound object is None."""

    #### 'BoundAction' interface ##############################################

    # The bound object.
    obj = Any

    # The optional trait on obj that we are synch'ed with.
    trait_name = Str

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **traits):
        """Initialise the object."""

        super(BoundAction, self).__init__(**traits)

        # Fake an obj change to set the initial state.
        self._obj_changed(None, self.obj)

    ###########################################################################
    # Traits handlers.
    ###########################################################################

    def _obj_changed(self, old, new):
        """Invoked when the bound object changes."""

        if old is not None:
            if self.trait_name:
                # Ignore any changes to the old object.
                old.on_trait_change(self._trait_changed, self.trait_name,
                        remove=True)

        enabled = False

        if new is not None:
            if self.trait_name:
                # Check for any changes on the new object.
                new.on_trait_change(self._trait_changed, self.trait_name)

                # Get the current state.
                if getattr(new, self.trait_name):
                    enabled = True
            else:
                enabled = True

        self.enabled = enabled

    def _trait_changed(self, new):
        """Invoked when the trait on the bound object changes."""

        self.enabled = new


class BoundWorkbenchAction(BoundAction):
    """A bound action whose object is being edited in a workbench editor.  The
    action is automatically rebound when the active editor changes."""

    #### 'BoundWorkbenchAction' interface #####################################

    # The type of the object that we will be enabled for.  If it is None then
    # we will be enabled for all types.
    trait_type = Any

    # The workbench window containing the action.
    window = Instance(WorkbenchWindow)

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **traits):
        """Initialise the object."""

        super(BoundWorkbenchAction, self).__init__(**traits)

        self.window.on_trait_change(self._editor_changed, 'active_editor')

        # Fake an editor change to set the initial state.
        self._editor_changed(self.window.active_editor)

    ###########################################################################
    # Traits handlers.
    ###########################################################################

    def _editor_changed(self, new):
        """Invoked when the active editor changes."""

        obj = None

        if new is not None:
            if self.trait_type is None:
                obj = new.obj
            elif isinstance(new.obj, self.trait_type):
                obj = new.obj

        self.obj = obj


class LabelAction(BoundWorkbenchAction):
    """ The LabelAction class is the base class for all actions that operate on
    a Label.
    """

    #### 'BoundWorkbenchAction' interface #####################################

    # The type of the object that we will be enabled for.
    trait_type = Label

    #### 'BoundAction' interface ##############################################

    # The bound object.
    obj = Instance(Label)


class LabelIncrementSizeAction(LabelAction):
    """ The LabelIncrementSizeAction class is a action that increases the size
    of a label's text.
    """

    #### 'Action' interface ###################################################

    # The name of the action.
    name = Unicode("&Increment size")

    ###########################################################################
    # 'Action' interface.
    ###########################################################################

    def perform(self, event):
        self.obj.increment_size(1)


class LabelDecrementSizeAction(LabelAction):
    """ The LabelDecrementSizeAction class is a action that decreases the size
    of a label's text.
    """

    #### 'Action' interface ###################################################

    # The name of the action.
    name = Unicode("&Decrement size")

    ###########################################################################
    # 'Action' interface.
    ###########################################################################

    def perform(self, event):
        self.obj.decrement_size(1)


class LabelNormalFontAction(LabelAction):
    """ The LabelNormalFontAction class is a action that sets a normal font for
    a label's text.
    """

    #### 'Action' interface ###################################################

    # The name of the action.
    name = Unicode("&Normal font")

    ###########################################################################
    # 'Action' interface.
    ###########################################################################

    def perform(self, event):
        self.obj.style = 'normal'


class LabelBoldFontAction(LabelAction):
    """ The LabelNormalFontAction class is a action that sets a bold font for a
    label's text.
    """

    #### 'Action' interface ###################################################

    # The name of the action.
    name = Unicode("&Bold font")

    ###########################################################################
    # 'Action' interface.
    ###########################################################################

    def perform(self, event):
        self.obj.style = 'bold'


class LabelItalicFontAction(LabelAction):
    """ The LabelNormalFontAction class is a action that sets an italic font
    for a label's text.
    """

    #### 'Action' interface ###################################################

    # The name of the action.
    name = Unicode("&Italic font")

    ###########################################################################
    # 'Action' interface.
    ###########################################################################

    def perform(self, event):
        self.obj.style = 'italic'
