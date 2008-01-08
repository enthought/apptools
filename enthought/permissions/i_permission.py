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
from enthought.traits.api import Bool, Interface, Str, Unicode


class IPermission(Interface):
    """The interface implemented by a permission.  A permission is the link
    between an application action and the current user - if the user has a
    permission attached to the action then the user is allowed to perform that
    action.
    """

    # The name of the permission.  By convention a dotted format is used for
    # the name with the name of the application being the first part.
    name = Str

    # A user friendly description of the permission.
    description = Unicode

    # Set if the current user has this permission.  This is typically used with
    # the enabled_when and visible_when traits of a TraitsUI Item object when
    # the permission instance has been placed in the TraitsUI context.
    granted = Bool

    # Set if the permission should be granted automatically when bootstrapping.
    # This is normally only ever set for permissions related to user management
    # and permissions.  The user manager determines exactly what is meant by
    # "bootstrapping" but it is usually when it determines that no user or
    # permissions information has been defined.
    bootstrap = Bool(False)
