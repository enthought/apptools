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
from traits.api import HasTraits, Instance, List, Unicode

# Local imports.
from apptools.permissions.permission import Permission


class Role(HasTraits):
    """This represents a role."""

    # The role name.
    name = Unicode

    # The role description.
    description = Unicode

    # The permissions that define the role.
    permissions = List(Instance(Permission))

    def __str__(self):
        """Return a user friendly representation."""

        s = self.description
        if not s:
            s = self.name

        return s


class Assignment(HasTraits):
    """This represents the assignment of roles to a user."""

    # The user name.
    user_name = Unicode

    # The user description.
    description = Unicode

    # The list of assigned roles.
    roles = List(Instance(Role))
