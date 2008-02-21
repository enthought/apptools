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
from enthought.traits.api import Bool, Event, HasTraits, implements, Instance
from enthought.traits.api import Int, Property, Unicode

# Local imports.
from i_undo_manager import IUndoManager
from script_manager import ScriptManager


class UndoManager(HasTraits):
    """ The UndoManager class is the default implementation of the
    IUndoManager interface.
    """

    implements(IUndoManager)

    #### 'IUndoManager' interface #############################################

    # This is the currently active command stack and may be None.  Typically it
    # is set when some sort of editor becomes active.
    active_stack = Instance('enthought.undo.api.ICommandStack')

    # This reflects the clean state of the currently active command stack.  It
    # is intended to support a "document modified" indicator in the GUI.  It is
    # maintained by the undo manager.
    active_stack_clean = Property(Bool)

    # This is set if commands are being recorded as a script.  It is maintained
    # by the undo manager.
    recording = Bool

    # This is the name of the command that can be redone.  It will be empty if
    # there is no command that can be redone.  It is maintained by the undo
    # manager.
    redo_name = Property(Unicode)

    # This is the text of the script currently being recorded (or the last
    # recorded script if none is currently being recorded).  It is updated
    # automatically as the user does, redos or undos commands.
    script = Property(Unicode)

    # This event is fired when the recorded script changes.  The value of the
    # event will be the UndoManager instance.
    script_updated = Event

    # This is the sequence number of the next command to be performed.  It is
    # incremented immediately before a command is invoked (by its 'do()'
    # method).
    sequence_nr = Int

    # This event is fired when the index of a command stack changes.  The value
    # of the event is the stack that has changed.  Note that it may not be the
    # active stack.
    stack_updated = Event

    # This is the name of the command that can be undone.  It will be empty if
    # there is no command that can be undone.  It is maintained by the undo
    # manager.
    undo_name = Property(Unicode)

    #### Private interface ####################################################

    # The script manager.
    _script_manager = Instance(ScriptManager)

    # Set if recoring has been paused temporarily during an undo.
    _was_recording = Bool

    ###########################################################################
    # 'IUndoManager' interface.
    ###########################################################################

    def begin_recording(self):
        """ Begin the recording of commands.  The 'script' trait is cleared and
        all subsequent commands are added to 'script'.  The recorded script is
        in a form that can be run immediately.  The 'recording' trait is
        updated appropriately.
        """

        self.recording = True
        self._script_manager.clear()
        self.script_updated = self

    def clear_recording(self):
        """ Clear any currently recorded script.  The 'recording' trait is
        updated appropriately.
        """

        self.recording = False
        self._script_manager.clear()
        self.script_updated = self

    def end_recording(self):
        """ End the recording of commands.  The 'recording' trait is updated
        appropriately.
        """

        self.recording = False

    def record_method(self, func, args, kwargs):
        """ Record the call of a method of a ScriptableObject instance and
        return the result.  This is intended to be used only by the scriptable
        decorator.
        """
        if self.recording:
            # Record the arguments before the function has a chance to modify
            # them.
            srec = self._script_manager.new_method(func, args, kwargs)
            result = func(*args, **kwargs)
            self._script_manager.add_method(srec, result, self.sequence_nr)

            self.script_updated = self
        else:
            result = func(*args, **kwargs)

        return result

    def record_trait_get(self, so, name, result):
        """ Record the get of a trait of a scriptable object.  This is intended
        to be used only by the Scriptable trait getter.
        """

        if self.recording:
            side_effects = self._script_manager.add_trait_get(so, name, result,
                    self.sequence_nr)

            # Don't needlessly fire the event if there are no side effects.
            if side_effects:
                self.script_updated = self

    def record_trait_set(self, so, name, value):
        """ Record the set of a trait of a scriptable object.  This is intended
        to be used only by the Scriptable trait getter.
        """

        if self.recording:
            self._script_manager.add_trait_set(so, name, value, self.sequence_nr)

            self.script_updated = self

    def redo(self):
        """ Redo the last undone command of the active command stack. """

        if self.active_stack is not None:
            self.active_stack.redo()

    def undo(self):
        """ Undo the last command of the active command stack. """

        if self.active_stack is not None:
            # Temporarily pause any recording so that the undos don't get
            # recorded.
            self._was_recording = self.recording
            self.recording = False

            self.active_stack.undo()

            if self._was_recording:
                # Resume recording.
                self._was_recording = False
                self.recording = True

                self.script_updated = self

    def undone(self, sequence_nr):
        """ Called when the command with the given sequence number has been
        undone.
        """

        if self._was_recording:
            self._script_manager.remove_call(sequence_nr)

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _active_stack_changed(self, new):
        """ Handle a different stack becoming active. """

        # Pretend that the stack contents have changed.
        self.stack_updated = new

    def _get_active_stack_clean(self):
        """ Get the current clean state. """

        if self.active_stack is None:
            active_stack_clean = True
        else:
            active_stack_clean = self.active_stack.clean

        return active_stack_clean

    def _get_redo_name(self):
        """ Get the current redo name. """

        if self.active_stack is None:
            redo_name = ""
        else:
            redo_name = self.active_stack.redo_name

        return redo_name

    def _get_script(self):
        """ Get the current script. """

        return self._script_manager.script

    def _get_undo_name(self):
        """ Get the current undo name. """

        if self.active_stack is None:
            undo_name = ""
        else:
            undo_name = self.active_stack.undo_name

        return undo_name

    def __script_manager_default(self):
        """ Create the initial script manager. """

        return ScriptManager()
