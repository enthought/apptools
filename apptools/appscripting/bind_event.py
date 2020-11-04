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
from traits.api import Any, HasTraits, provides, Str

# Local imports.
from .i_bind_event import IBindEvent


@provides(IBindEvent)
class BindEvent(HasTraits):
    """The default implementation of the bind event interface."""



    #### 'IBindEvent' interface ###############################################

    # This is the name being bound or unbound.
    name = Str

    # This is the object being bound to the name.  It is None if the name is
    # being unbound.
    obj = Any
