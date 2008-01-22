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
from enthought.traits.api import HasTraits, Instance, List, Unicode

# Local imports.
from enthought.permissions.i_permission import IPermission


class Role(HasTraits):
    """This represents a role."""

    # The role name.
    name = Unicode

    # The role description.
    description = Unicode

    # The permissions that define the role.
    permissions = List(Instance(IPermission))


class Assignment(HasTraits):
    """This represents the assignment of roles to a user."""

    # The user name.
    user_name = Unicode

    # The list of assigned roles.
    roles = List(Instance(Role))
