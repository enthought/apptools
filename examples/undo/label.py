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
from enthought.traits.api import Enum, Instance, Int, Unicode
from enthought.undo.api import AbstractCommand
from enthought.undo.api import scriptable, Scriptable, ScriptableObject


class Label(ScriptableObject):
    """ The Label class implements the data model for a label. """

    #### 'Label' interface ####################################################

    # The name.
    name = Unicode
    
    # The size in points.
    size = Int(18)
    
    # The style.
    style = Scriptable(Enum('normal', 'bold', 'italic'))

    ###########################################################################
    # 'Label' interface.
    ###########################################################################

    @scriptable
    def increment_size(self, by):
        """ Increment the current font size.  This demonstrates a scriptable
        method.
        """

        self.size += by

    @scriptable
    def decrement_size(self, by):
        """ decrement the current font size.  This demonstrates a scriptable
        method.
        """

        self.size -= by


class LabelIncrementSizeCommand(AbstractCommand):
    """ The LabelIncrementSizeCommand class is a command that increases the
    size of a label's text.  This command will merge multiple increments
    togther.
    """

    #### 'ICommand' interface #################################################

    # The data being operated on.
    data = Instance(Label)

    # The name of the command.
    name = Unicode("&Increment size")

    #### Private interface ####################################################

    _incremented_by = Int

    ###########################################################################
    # 'ICommand' interface.
    ###########################################################################

    def do(self):
        self.data.increment_size(1)
        self._incremented_by = 1

    def merge(self, other):
        # We can merge if the other command is the same type (or a sub-type).
        if isinstance(other, type(self)):
            self._incremented_by += 1
            merged = True
        else:
            merged = False

        return merged

    def redo(self):
        self.data.increment_size(self._incremented_by)

    def undo(self):
        self.data.decrement_size(self._incremented_by)


class LabelDecrementSizeCommand(AbstractCommand):
    """ The LabelDecrementSizeCommand class is a command that decreases the
    size of a label's text.  This command will merge multiple decrements
    togther.
    """

    #### 'ICommand' interface #################################################

    # The data being operated on.
    data = Instance(Label)

    # The name of the command.
    name = Unicode("&Decrement size")

    #### Private interface ####################################################

    _decremented_by = Int

    ###########################################################################
    # 'ICommand' interface.
    ###########################################################################

    def do(self):
        self.data.decrement_size(1)
        self._decremented_by = 1

    def merge(self, other):
        # We can merge if the other command is the same type (or a sub-type).
        if isinstance(other, type(self)):
            self._decremented_by += 1
            merged = True
        else:
            merged = False

        return merged

    def redo(self):
        self.data.decrement_size(self._decremented_by)

    def undo(self):
        self.data.increment_size(self._decremented_by)


class LabelNormalFontCommand(AbstractCommand):
    """ The LabelNormalFontCommand class is a command that sets a normal font
    for a label's text.
    """

    #### 'ICommand' interface #################################################

    # The data being operated on.
    data = Instance(Label)

    # The name of the command.
    name = Unicode("&Normal font")

    ###########################################################################
    # 'ICommand' interface.
    ###########################################################################

    def do(self):
        # Save the old value.
        self._saved = self.data.style

        # Calling redo() is a convenient way to update the model now that the
        # old value is saved.
        self.redo()

    def redo(self):
        self.data.style = 'normal'

    def undo(self):
        self.data.style = self._saved


class LabelBoldFontCommand(AbstractCommand):
    """ The LabelNormalFontCommand class is a command that sets a bold font for
    a label's text.
    """

    #### 'ICommand' interface #############################################

    # The data being operated on.
    data = Instance(Label)

    # The name of the command.
    name = Unicode("&Bold font")

    ###########################################################################
    # 'ICommand' interface.
    ###########################################################################

    def do(self):
        # Save the old value.
        self._saved = self.data.style

        # Calling redo() is a convenient way to update the model now that the
        # old value is saved.
        self.redo()

    def redo(self):
        self.data.style = 'bold'

    def undo(self):
        self.data.style = self._saved


class LabelItalicFontCommand(AbstractCommand):
    """ The LabelNormalFontCommand class is a command that sets an italic font
    for a label's text.
    """

    #### 'ICommand' interface #################################################

    # The data being operated on.
    data = Instance(Label)

    # The name of the command.
    name = Unicode("&Italic font")

    ###########################################################################
    # 'ICommand' interface.
    ###########################################################################

    def do(self):
        # Save the old value.
        self._saved = self.data.style

        # Calling redo() is a convenient way to update the model now that the
        # old value is saved.
        self.redo()

    def redo(self):
        self.data.style = 'italic'

    def undo(self):
        self.data.style = self._saved
