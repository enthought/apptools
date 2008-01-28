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
from enthought.pyface.action.api import Action
from enthought.traits.api import Bool, Event, HasTraits, implements, \
        Instance, List

# Local imports.
from enthought.permissions.i_user import IUser
from enthought.permissions.i_user_manager import IUserManager
from enthought.permissions.permission import Permission
from enthought.permissions.permissions_manager import PermissionsManager
from enthought.permissions.secure_proxy import SecureProxy
from i_user_database import IUserDatabase


class UserManager(HasTraits):
    """The default user manager implementation."""

    implements(IUserManager)

    #### 'IUserManager' interface #############################################

    management_actions = List(Instance(Action))

    user = Instance(IUser)

    user_actions = List(Instance(Action))

    user_authenticated = Event(IUser)

    #### 'UserManger' interface ###############################################

    # The user database.
    user_db = Instance(IUserDatabase)

    ###########################################################################
    # 'IUserManager' interface.
    ###########################################################################

    def bootstrapping(self):
        """Return True if we are bootstrapping, ie. no users have been defined.
        """

        return self.user_db.bootstrapping()

    def authenticate_user(self):
        """Authenticate the user."""

        if self.user_db.authenticate_user(self.user):
            self.user.authenticated = True

            # Tell the policy manager before everybody else.
            PermissionsManager.policy_manager.load_policy(self.user)

            self.user_authenticated = self.user

    def unauthenticate_user(self):
        """Unauthenticate the user."""

        if self.user.authenticated and self.user_db.unauthenticate_user(self.user):
            self.user.authenticated = False

            # Tell the policy manager before everybody else.
            PermissionsManager.policy_manager.load_policy(None)

            self.user_authenticated = None

    def select_user(self, name):
        """Select a user."""

        return self.user_db.select_user(name)

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _management_actions_default(self):
        """Return the list of management actions."""

        user_db = self.user_db
        actions = []

        if user_db.can_add_user:
            perm = Permission(name='ets.permissions.management.add_user',
                    description=u"Add users", bootstrap=True)
            act = Action(name='&Add a User...', on_perform=user_db.add_user)

            actions.append(SecureProxy(act, permissions=[perm], show=False))

        if user_db.can_modify_user:
            perm = Permission(name='ets.permissions.management.modify_user',
                    description=u"Modify users", bootstrap=True)
            act = Action(name='&Modify a User...',
                    on_perform=user_db.modify_user)

            actions.append(SecureProxy(act, permissions=[perm], show=False))

        if user_db.can_delete_user:
            perm = Permission(name='ets.permissions.management.delete_user',
                    description=u"Delete users", bootstrap=True)
            act = Action(name='&Delete a User...',
                    on_perform=user_db.delete_user)

            actions.append(SecureProxy(act, permissions=[perm], show=False))

        return actions

    def _user_actions_default(self):
        """Return the list of user actions."""

        user_db = self.user_db
        actions = []

        if user_db.can_change_password:
            perm = Permission(name='ets.permissions.management.change_password',
                    description=u"Change user's password")
            act = Action(name='&Change Password...',
                    on_perform=lambda: user_db.change_password(self.user))

            actions.append(SecureProxy(act, permissions=[perm]))

        return actions

    def _user_default(self):
        """Return the default current user."""

        return self.user_db.user_factory()

    def _user_db_default(self):
        """Return the default user database."""

        from user_database import UserDatabase

        return UserDatabase()
