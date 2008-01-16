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


# Standard library imports.
import os

# Enthought library imports.
from enthought.pyface.api import confirm, error, information, YES
from enthought.traits.api import Dict, HasTraits, implements, Instance, \
        Password, Unicode
from enthought.traits.ui.api import Handler, Item, View
from enthought.traits.ui.menu import Action, OKCancelButtons

# Local imports.
from i_user_database import IUserDatabase
from persistent import Persistent, PersistentError


class UserAccount(HasTraits):
    """This represents a single account in the persisted user database."""

    #### 'UserAccount' interface ##############################################

    # The name the user uses to identify themselves.
    name = Unicode

    # A description of the user (typically their full name).
    description = Unicode

    # The user's password.
    password = Unicode


class UserDb(HasTraits):
    """This is the persisted user database."""

    #### 'UserDb' interface ###################################################

    # The dictionary of user accounts.
    users = Dict


class _ViewUserAccount(UserAccount):
    """This represents a single account when in a view."""

    #### 'UserAccount' interface ##############################################

    # The password
    password = Password

    #### '_ViewUserAccount' interface #########################################

    # The password confirmation.
    confirm_password = Password

    # The user database.
    user_db = Instance('UserDatabase')


class _UserAccountHandler(Handler):
    """The base traits handler for user account views."""

    ###########################################################################
    # 'Handler' interface.
    ###########################################################################

    def close(self, info, is_ok):
        """Reimplemented to validate the data."""

        # If the user cancelled then close the dialog.
        if not is_ok:
            return True

        # Validate the form, only closing the dialog if the form is valid.
        return self.validate(self._user_account(info))

    ###########################################################################
    # '_UserAccountHandler' interface.
    ###########################################################################

    def validate(self, vuac):
        """This must be reimplemented to validate the given object and return
        True if there were no problems."""

        raise NotImplementedError

    @staticmethod
    def error(msg):
        """Display an error message to the user."""

        error(None, msg)

    @staticmethod
    def inform(msg):
        """Display an information message to the user."""

        information(None, msg)

    def search(self, vuac, name, users):
        """This must be reimplemented to search the user database and update
        the viewed object appropriately."""

        raise NotImplementedError

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _search_clicked(self, info):
        """Invoked by the "Search" button."""

        # Get the user name and a read-only copy of the dictionary of users.
        vuac = self._user_account(info)
        db = vuac.user_db.readonly_copy()

        if db is not None:
            name = vuac.name.strip()

            if name:
                self.search(vuac, vuac.name.strip(), db.users)
            else:
                self.error("Please give a user name to search for.")

    ###########################################################################
    # Private interface.
    ###########################################################################

    @staticmethod
    def _user_account(info):
        """Return the user account instance being handled."""

        return info.ui.context['object']


class _AddUserAccountHandler(_UserAccountHandler):
    """The traits handler for the add user account view."""

    ###########################################################################
    # '_UserAccountHandler' interface.
    ###########################################################################

    def validate(self, vuac):
        """Validate the given object and return True if there were no problems.
        """

        MIN_PASSWORD_LEN = 6

        if not vuac.name.strip():
            self.error("A user name must be given.")
            return False

        if vuac.password != vuac.confirm_password:
            self.error("The passwords do not match.")
            return False

        if not vuac.password:
            self.error("A password must be given.")
            return False

        if len(vuac.password) < MIN_PASSWORD_LEN:
            self.error("The password must be at least %d characters long." % MIN_PASSWORD_LEN)
            return False

        return True

    def search(self, vuac, name, users):
        """Search the user database to see if a user already exists."""

        # See if there is a user with the name.
        if users.has_key(name):
            self.error("A user called \"%s\" already exists." % name)
        else:
            self.inform("A user called \"%s\" doesn't currently exist." % name)


class _ModifyUserAccountHandler(_AddUserAccountHandler):
    """The traits handler for the modify user account view that validates the
    data."""

    ###########################################################################
    # '_UserAccountHandler' interface.
    ###########################################################################

    def search(self, vuac, name, users):
        """Search the user database and update the viewed object appropriately.
        """

        # See if there is a user with the name.
        try:
            uac = users[name]
        except KeyError:
            # Find the first user that starts with the name.
            for n, uac in users.items():
                if n.startswith(name):
                    break
            else:
                if name:
                    self.error("There is no user whose name starts with \"%s\"." % name)
                else:
                    self.error("No users have been defined.")

                return

        # Update the viewed object.
        vuac.name = uac.name
        vuac.description = uac.description
        vuac.password = vuac.confirm_password = uac.password


class _DeleteUserAccountHandler(_ModifyUserAccountHandler):
    """The traits handler for the delete user account view."""

    ###########################################################################
    # '_UserAccountHandler' interface.
    ###########################################################################

    def validate(self, vuac):
        """Validate the given object and return True if there were no problems.
        """

        if not vuac.name.strip():
            self.error("A user name must be given.")
            return False

        return True


class _UserAccountView(View):
    """The base view for handling user accounts."""

    #### 'View' interface #####################################################

    kind = 'modal'

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _buttons_default(self):
        """Return the view's buttons."""

        # Create an action that will search the database.
        buttons = [Action(name="Search")]
        buttons.extend(OKCancelButtons)

        return buttons


class _AddUserAccountView(_UserAccountView):
    """A view to handle adding a user account."""

    #### 'View' interface #####################################################

    title = "Add a user"

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **traits):
        """Initialise the object."""

        super(_AddUserAccountView, self).__init__(Item(name='name'),
                Item(name='description'), Item(name='password'),
                Item(name='confirm_password'), **traits)


class _ModifyUserAccountView(_AddUserAccountView):
    """A view to handle modifying a user account."""

    #### 'View' interface #####################################################

    title = "Modify a user"


class _DeleteUserAccountView(_UserAccountView):
    """A view to handle deleting a user account."""

    #### 'View' interface #####################################################

    title = "Delete a user"

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **traits):
        """Initialise the object."""

        super(_DeleteUserAccountView, self).__init__(Item(name='name'),
                Item(name='description', style='readonly'), **traits)


class _LoginUser(HasTraits):
    """This represents the login data and view."""

    # The user name.
    name = Unicode

    # The user password.
    password = Password

    # The default view.
    traits_view = View(Item(name='name'), Item(name='password'),
            title="Login", kind='modal', buttons=OKCancelButtons)


class UserDatabase(HasTraits):
    """This is the default implementation of a user database.  It is good
    enough to be used in a cooperative environment (ie. where real access
    control is not required).  In an enterprise environment the user database
    should be replaced with one that interacts with some secure directory
    service."""

    implements(IUserDatabase)

    #### 'IUserDatabase' interface ############################################

    can_add_user = True

    can_modify_user = True

    can_delete_user = True

    #### Private interface ###################################################

    # The persisted database.
    _db = Instance(Persistent)

    ###########################################################################
    # 'IUserDatabase' interface.
    ###########################################################################

    def authenticate_user(self, user):
        """Authenticate a user."""

        # Get the login details.
        name = user.name

        if not name:
            name = os.environ.get('USER', '')

        lu = _LoginUser(name=name)

        if not lu.edit_traits().result:
            return False

        # Get the users.
        db = self.readonly_copy()

        if db is None:
            return False

        # Get the user account and compare passwords.
        try:
            uac = db.users[lu.name]

            if uac.password != lu.password:
                uac = None
        except KeyError:
            uac = None

        if uac is None:
            # It's bad security to give too much information...
            error(None, "The user name or password is invalid.")
            return False

        # Copy the relevant parts of the user account.
        user.name = uac.name
        user.description = uac.description

        return True

    def unauthenticate_user(self, user):
        """Unauthenticate a user."""

        # There is nothing to do to unauthenticate so it is always successful.
        return True

    def add_user(self):
        """Add a user."""

        # Get the data from the user.
        vuac = _ViewUserAccount(user_db=self)
        view = _AddUserAccountView()
        handler = _AddUserAccountHandler()

        if vuac.edit_traits(view=view, handler=handler).result:
            uac = UserAccount(name=vuac.name.strip(),
                    description=vuac.description, password=vuac.password)

            # Add the data to the database.
            try:
                self._db.lock()

                try:
                    data = self._db.read()

                    if data.users.has_key(uac.name):
                        raise PersistentError("The user \"%s\" already exists." % uac.name)

                    data.users[uac.name] = uac
                    self._db.write(data)
                finally:
                    self._db.unlock()
            except PersistentError, e:
                error(None, str(e))

    def modify_user(self):
        """Modify a user."""

        # Get the data from the user.
        vuac = _ViewUserAccount(user_db=self)
        view = _ModifyUserAccountView()
        handler = _ModifyUserAccountHandler()

        if vuac.edit_traits(view=view, handler=handler).result:
            uac = UserAccount(name=vuac.name.strip(),
                    description=vuac.description, password=vuac.password)

            # Update the data in the database.
            try:
                self._db.lock()

                try:
                    data = self._db.read()

                    if not data.users.has_key(uac.name):
                        raise PersistentError("The user \"%s\" doesn't exist." % uac.name)

                    data.users[uac.name] = uac
                    self._db.write(data)
                finally:
                    self._db.unlock()
            except PersistentError, e:
                error(None, str(e))

    def delete_user(self):
        """Delete a user."""

        # Get the data from the user.
        vuac = _ViewUserAccount(user_db=self)
        view = _DeleteUserAccountView()
        handler = _DeleteUserAccountHandler()

        if vuac.edit_traits(view=view, handler=handler).result:
            name = vuac.name.strip()

            # Delete the data from the database.
            try:
                self._db.lock()

                try:
                    data = self._db.read()

                    if not data.users.has_key(name):
                        raise PersistentError("The user \"%s\" doesn't exist." % name)

                    if confirm(None, "Are you sure you want to delete the user \"%s\"?" % name) == YES:
                        del data.users[name]
                        self._db.write(data)
                finally:
                    self._db.unlock()
            except PersistentError, e:
                error(None, str(e))

    ###########################################################################
    # 'UserDatabase' interface.
    ###########################################################################

    def readonly_copy(self):
        """Return the current user database (which should not be modified)."""

        try:
            self._db.lock()

            try:
                data = self._db.read()
            finally:
                self._db.unlock()
        except PersistentError, e:
            error(None, str(e))
            data = None

        return data

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def __db_default(self):
        """Return the default persisted database."""

        return Persistent(UserDb, 'ets_perms_userdb', "the user database")
