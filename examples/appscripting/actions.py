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
from enthought.traits.api import Any, Unicode
from enthought.pyface.action.api import Action


class BoundAction(Action):
    """An action with bound data.  The action is automatically disabled if the
    bound data is None."""

    #### 'BoundAction' interface ##############################################

    # The bound data.
    data = Any


class BoundWorkbenchAction(BoundAction):
    """A bound action whose data is being edited in a workbench editor.  The
    action is automatically rebound when the active editor changes."""

    #### 'BoundWorkbenchAction' interface #####################################

    # The workbench window containing the action.
    window = Instance(WorkbenchWindow)


class LabelIncrementSizeAction(BoundWorkbenchAction):
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
        self.data.increment_size(1)


class LabelDecrementSizeAction(BoundWorkbenchAction):
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
        self.data.decrement_size(1)


class LabelNormalFontAction(BoundWorkbenchAction):
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
        self.data.style = 'normal'


class LabelBoldFontAction(BoundWorkbenchAction):
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
        self.data.style = 'bold'


class LabelItalicFontAction(BoundWorkbenchAction):
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
        self.data.style = 'italic'
