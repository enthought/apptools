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
from enthought.permissions.secure_proxy import SecureProxy
from i_user_database import IUserDatabase


class UserManager(HasTraits):
    """The default user manager implementation."""

    implements(IUserManager)

    #### 'IUserManager' interface #############################################

    bootstrap_perms = Bool(True)

    management_actions = List(Instance(Action))

    user = Instance(IUser)

    user_authenticated = Event(IUser)

    #### 'UserManager' interface ##############################################

    # The user database.
    user_db = Instance(IUserDatabase)

    ###########################################################################
    # 'IUserManager' interface.
    ###########################################################################

    def authenticate_user(self, user=None):

        if user is None:
            user = self.user

        # FIXME: For the moment do it unconditionally.
        user.authenticated = True

        self.user = user
        self.user_authenticated = user

    def unauthenticate_user(self):

        self.user.authenticated = False
        self.user_authenticated = None

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _user_default(self):
        """Return the default current user."""

        from enthought.permissions.user import User

        return User()

    def _management_actions_default(self):
        """Return the list of management actions."""

        user_db = self.user_db
        actions = []

        if user_db.can_add_user:
            perm = Permission(name='ets.permissions.management.add_user',
                    description=u"Add users", bootstrap=True)
            act = Action(name='&Add a user...', on_perform=user_db.add_user)

            actions.append(SecureProxy(act, perms=[perm], show=False))

        if user_db.can_modify_user:
            perm = Permission(name='ets.permissions.management.modify_user',
                    description=u"Modify users", bootstrap=True)
            act = Action(name='&Modify a user...',
                    on_perform=user_db.modify_user)

            actions.append(SecureProxy(act, perms=[perm], show=False))

        if user_db.can_delete_user:
            perm = Permission(name='ets.permissions.management.delete_user',
                    description=u"Delete users", bootstrap=True)
            act = Action(name='&Delete a user...',
                    on_perform=user_db.delete_user)

            actions.append(SecureProxy(act, perms=[perm], show=False))

        return actions

    def _user_db_default(self):
        """Return the default user database."""

        from user_database import UserDatabase

        return UserDatabase()
