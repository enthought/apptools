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
from pyface.action.api import Group, MenuManager
from traits.api import Unicode

# Local imports.
from apptools.permissions.package_globals import get_permissions_manager
from .login_action import LoginAction
from .logout_action import LogoutAction


class UserMenuManager(MenuManager):
    """A menu that contains all the actions related to users and permissions.
    """

    #### 'MenuManager' interface ##############################################

    id = 'User'

    name = Unicode("&User")

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **traits):
        """Initialise the object."""

        pm = get_permissions_manager()

        # Put them in a group so we can optionally append (because the PyFace
        # API doesn't do what you expect with append()).
        group = Group()

        group.append(LoginAction())

        for act in pm.user_manager.user_actions:
            group.append(act)

        group.append(LogoutAction())

        for act in pm.user_manager.management_actions:
            group.append(act)

        for act in pm.policy_manager.management_actions:
            group.append(act)

        super(UserMenuManager, self).__init__(group, **traits)
