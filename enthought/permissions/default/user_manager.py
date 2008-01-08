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


# Standard library imports.
import os

# Enthought library imports.
from enthought.pyface.action.api import Action
from enthought.traits.api import Bool, Event, HasTraits, implements, \
        Instance, List, Str, Unicode

# Local imports.
from enthought.permissions.i_user import IUser
from enthought.permissions.i_user_manager import IUserManager
from enthought.permissions.permission import Permission
from enthought.permissions.persistent import Persistent
from enthought.permissions.secure_proxy import SecureProxy
from user import DefaultUser


class _Role(HasTraits):
    """This represents a role as a collection of permission IDs."""

    # The name of the role.
    name = Unicode

    # A description of the role.
    description = Unicode

    # The list of the names of the permisions (ie. not the permissions
    # themselves) that define the role.
    perm_names = List(Str)


class _UserAccount(HasTraits):
    """This represents a single user account in the user database."""

    # The name the user uses to identify themselves.
    name = Unicode

    # A description of the user (typically their full name).
    description = Unicode

    # The user's password (in clear text).
    password = Unicode


class _UserDatabase(Persistent):
    """This implements a simple file based user database used by the default
    user manager.  It is good enough to allow roles and responsibilities to be
    used in a cooperative environment (ie. where real access control is not
    required).  In an enterprise environment the default user manager should be
    replaced with one that interacts with some secure directory service."""

    # The list of users.
    users = List(_UserAccount)


class DefaultUserManager(HasTraits):
    """The default user manager implementation."""

    implements(IUserManager)

    #### 'IUserManager' interface #############################################

    bootstrap_perms = Bool(True)

    management_actions = List(Instance(Action))

    user = Instance(IUser)

    user_authenticated = Event(IUser)

    #### Private interface ####################################################

    # The user database.
    _user_db = Instance(_UserDatabase)

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
    # Private interface.
    ###########################################################################

    def _add_user(self):
        """TODO"""

        from enthought.pyface.api import information

        information(None, "This will eventually implement a TraitsUI based GUI for adding users.")

    def _modify_user(self):
        """TODO"""

        from enthought.pyface.api import information

        information(None, "This will eventually implement a TraitsUI based GUI for modifying users.")

    def _delete_user(self):
        """TODO"""

        from enthought.pyface.api import information

        information(None, "This will eventually implement a TraitsUI based GUI for deleting users.")

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _user_default(self):
        """Return the default current user."""

        # Create a default user with a suggested name corresponding to their
        # current name.
        return DefaultUser(name=os.environ.get('USER', ''))

    def _management_actions_default(self):
        """Return the list of management actions."""

        add_perm = Permission(name='ets.permissions.management.add_user',
                description=u"Add users", bootstrap=True)

        add = Action(name='&Add a user...', on_perform=self._add_user)
        add = SecureProxy(add, perms=[add_perm], show=False)

        modify_perm = Permission(name='ets.permissions.management.modify_user',
                description=u"Modify users", bootstrap=True)

        modify = Action(name='&Modify a user...', on_perform=self._modify_user)
        modify = SecureProxy(modify, perms=[modify_perm], show=False)

        delete_perm = Permission(name='ets.permissions.management.delete_user',
                description=u"Delete users", bootstrap=True)

        delete = Action(name='&Delete a user...', on_perform=self._delete_user)
        delete = SecureProxy(delete, perms=[delete_perm], show=False)

        return [add, modify, delete]

    def __user_db_default(self):
        """Return the user database."""

        return _UserDatabase('ets_perms_userdb', 'ETS_PERMS_USERDB')
