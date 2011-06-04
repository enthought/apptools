#-------------------------------------------------------------------------------
#
#  Traits UI editor for displaying Enable Components.
#
#  Written by: David Morrill
#
#  Date: 07/30/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Traits UI editor for displaying Enable Components.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from traitsui.wx.editor \
    import Editor

from traitsui.wx.basic_editor_factory \
    import BasicEditorFactory

from enable.wx_backend.api \
    import Window

#-------------------------------------------------------------------------------
#  '_EnableEditor' class:
#-------------------------------------------------------------------------------

class _EnableEditor ( Editor ):
    """ Traits UI editor for displaying Enable Components.
    """

    # Override the default value to allow the control to be resizable:
    scrollable = True

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._window = Window( parent, -1,
                               component = self.value,
                               bg_color  = ( 0.698, 0.698, 0.698, 1.0 ) )
        self.control = self._window.control
        self.control.SetSize( wx.Size( 300, 300 ) )

        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self._window.component = self.value

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for Enable component editors:
class EnableEditor ( BasicEditorFactory ):

    # The editor class to be created:
    klass = _EnableEditor

