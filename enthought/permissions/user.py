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
# Description: <Enthought permissions package component>
#------------------------------------------------------------------------------


# Enthought library imports.
from enthought.traits.api import Bool, HasTraits, implements, Unicode

# Local imports.
from i_user import IUser


class User(HasTraits):
    """The default user implementation."""

    implements(IUser)

    #### 'IUser' interface ####################################################

    name = Unicode

    authenticated = Bool(False)

    description = Unicode
