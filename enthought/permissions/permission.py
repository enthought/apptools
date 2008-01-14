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
from enthought.traits.api import Bool, HasTraits, implements, Property, Str, \
        Unicode

# Locals imports.
from i_permission import IPermission
from permissions_manager import PermissionsManager


class Permission(HasTraits):
    """The default implementation of a permission.  It will automatically add
    itself to the current permissions policy's list of permissions.
    """

    implements(IPermission)

    #### 'IPermission' interface ##############################################

    name = Str

    description = Unicode

    granted = Property

    bootstrap = Bool(False)

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **traits):
        """Initialise the object."""

        super(Permission, self).__init__(**traits)

        # Tell the current permissions policy.
        PermissionsManager.policy.perms.append(self)

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _get_granted(self):
        """Check the user has this permission."""

        return PermissionsManager.policy.check_perms(self)
