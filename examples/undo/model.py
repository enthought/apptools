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
# Description: <Enthought undo package component>
#------------------------------------------------------------------------------


# Enthought library imports.
from enthought.traits.api import Enum, Int, Unicode
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
