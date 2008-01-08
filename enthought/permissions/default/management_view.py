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
# Description: <Enthought permissions package component>
#------------------------------------------------------------------------------


# Enthought library imports.
from enthought.traits.api import HasTraits, implements

# Local imports.
from i_management_view import IManagementView


class DefaultManagementView(HasTraits):
    """The default management view implementation."""

    implements(IManagementView)

    def __call__(self, user_manager):
        """TODO"""

        from enthought.pyface.api import information

        information(None, "This will eventually implement a TraitsUI based GUI for managing users and roles.")
