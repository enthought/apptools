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
from traits.api import Bool, HasTraits, Property, Str, Unicode

# Locals imports.
from .package_globals import get_permissions_manager


class Permission(HasTraits):
    """A permission is the link between an application action and the current
    user - if the user has a permission attached to the action then the user is
    allowed to perform that action."""

    #### 'Permission' interface ###############################################

    # The id of the permission.  By convention a dotted format is used for the
    # id with the id of the application being the first part.
    id = Str

    # A user friendly description of the permission.
    description = Unicode

    # Set if the current user has this permission.  This is typically used with
    # the enabled_when and visible_when traits of a TraitsUI Item object when
    # the permission instance has been placed in the TraitsUI context.
    granted = Property

    # Set if the permission should be granted automatically when bootstrapping.
    # This is normally only ever set for permissions related to user management
    # and permissions.  The user manager determines exactly what is meant by
    # "bootstrapping" but it is usually when it determines that no user or
    # permissions information has been defined.
    bootstrap = Bool(False)

    # Set if the permission has been defined by application code rather than as
    # a result of loading the policy database.
    application_defined = Bool(True)

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **traits):
        """Initialise the object."""

        super(Permission, self).__init__(**traits)

        # Register the permission.
        get_permissions_manager().policy_manager.register_permission(self)

    def __str__(self):
        """Return a user friendly representation."""

        s = self.description
        if not s:
            s = self.id

        return s

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _get_granted(self):
        """Check the user has this permission."""

        return get_permissions_manager().check_permissions(self)


class ManagePolicyPermission(Permission):
    """The standard permission for managing permissions policies."""

    #### 'Permission' interface ###############################################

    id = Str('ets.permissions.manage_policy')

    description = Unicode(u"Manage permissions policy")

    bootstrap = Bool(True)


class ManageUsersPermission(Permission):
    """The standard permission for managing permissions users."""

    #### 'Permission' interface ###############################################

    id = Str('ets.permissions.manage_users')

    description = Unicode(u"Manage users")

    bootstrap = Bool(True)
