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
from pyface.api import confirm, error, YES
from traits.api import Bool, Dict, HasTraits, provides, Instance, \
        List, Password, Property, Unicode
from traitsui.api import Handler, Item, View
from traitsui.menu import Action, OKCancelButtons

# Local imports.
from apptools.permissions.i_user import IUser
from .i_user_database import IUserDatabase
from .i_user_storage import IUserStorage, UserStorageError
from .select_user import select_user


@provides(IUser)
class _LoginUser(HasTraits):
    """This represents the login data and view."""

    #### '_LoginUser' interface ###############################################

    # The user name.
    name = Unicode

    # The user password.
    password = Password

    # The default view.
    traits_view = View(Item(name='name'), Item(name='password'),
            title="Login", kind='modal', buttons=OKCancelButtons)


class _ChangePassword(HasTraits):
    """This represents the change password data and view."""

    #### '_ChangePassword' interface ##########################################

    # The user name.
    name = Unicode

    # The new user password.
    new_password = Password

    # The confirmed new user password.
    confirm_new_password = Password

    # The default view.
    traits_view = View(Item(name='name', style='readonly'),
            Item(name='new_password'), Item(name='confirm_new_password'),
            title="Change password", kind='modal', buttons=OKCancelButtons)


class _ViewUserAccount(HasTraits):
    """This represents a single account when in a view."""

    #### '_ViewUserAccount' interface #########################################

    # The name the user uses to identify themselves.
    name = Unicode

    # A description of the user (typically their full name).
    description = Unicode

    # The password
    password = Password

    # The password confirmation.
    confirm_password = Password

    # The user database.
    user_db = Instance(IUserDatabase)


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
        """Validate the given object and return True if there were no problems.
        """

        if not vuac.name.strip():
            self.error("A user name must be given.")
            return False

        return True

    @staticmethod
    def error(msg):
        """Display an error message to the user."""

        error(None, msg)

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _search_clicked(self, info):
        """Invoked by the "Search" button."""

        # Get the user name.
        vuac = self._user_account(info)

        name, description = vuac.user_db._select_user(vuac.name)
        if not name:
            return

        # Update the viewed object.
        vuac.name = name
        vuac.description = description
        vuac.password = vuac.confirm_password = ''

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

        if not super(_AddUserAccountHandler, self).validate(vuac):
            return False

        if not _validate_password(vuac.password, vuac.confirm_password):
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


class User(HasTraits):
    """The user implementation.  We don't store any extra information other
    than that defined by IUser."""



    #### 'IUser' interface ####################################################

    name = Unicode

    authenticated = Bool(False)

    description = Unicode

    blob = Dict


@provides(IUserDatabase)
class UserDatabase(HasTraits):
    """This implements a user database that supports IUser for the default user
    manager (ie. using password authorisation) except that it leaves the actual
    access of the data to an implementation of IUserStorage."""



    #### 'IUserDatabase' interface ############################################

    can_change_password = Property

    can_add_user = Property

    can_modify_user = Property

    can_delete_user = Property

    user_storage = Instance(IUserStorage)

    #### Private interface ####################################################

    # Set if updating the user blob internally.
    _updating_blob_internally = Bool(False)

    ###########################################################################
    # 'IUserDatabase' interface.
    ###########################################################################

    def bootstrapping(self):
        """See if we are bootstrapping."""

        try:
            bootstrap = self.user_storage.is_empty()
        except UserStorageError:
            # Suppress the error and assume it isn't empty.
            bootstrap = False

        return bootstrap

    def authenticate_user(self, user):
        """Authenticate a user."""

        # Get the login details.
        name = user.name
        lu = _LoginUser(name=name)

        if not lu.edit_traits().result:
            return False

        # Get the user account and compare passwords.
        try:
            name, description, blob = self.user_storage.authenticate_user(
                    lu.name.strip(), lu.password)
        except UserStorageError as e:
            self._us_error(e)
            return False

        # Update the user details.
        user.name = name
        user.description = description

        # Suppress the trait notification.
        self._updating_blob_internally = True
        user.blob = blob
        self._updating_blob_internally = False

        return True

    def unauthenticate_user(self, user):
        """Unauthenticate a user."""

        return self.user_storage.unauthenticate_user(user)

    def change_password(self, user):
        """Change a user's password."""

        # Get the new password.
        name = user.name
        np = _ChangePassword(name=name)

        if not np.edit_traits().result:
            return

        # Validate the password.
        if not _validate_password(np.new_password, np.confirm_new_password):
            return

        # Update the password in the database.
        try:
            self.user_storage.update_password(name, np.new_password)
        except UserStorageError as e:
            self._us_error(e)

    def add_user(self):
        """Add a user."""

        # Get the data from the user.
        vuac = _ViewUserAccount(user_db=self)
        view = _AddUserAccountView()
        handler = _AddUserAccountHandler()

        if vuac.edit_traits(view=view, handler=handler).result:
            # Add the data to the database.
            try:
                self.user_storage.add_user(vuac.name.strip(), vuac.description,
                        vuac.password)
            except UserStorageError as e:
                self._us_error(e)

    def modify_user(self):
        """Modify a user."""

        # Get the data from the user.
        vuac = _ViewUserAccount(user_db=self)
        view = _ModifyUserAccountView()
        handler = _UserAccountHandler()

        if vuac.edit_traits(view=view, handler=handler).result:
            # Update the data in the database.
            try:
                self.user_storage.modify_user(vuac.name.strip(),
                        vuac.description, vuac.password)
            except UserStorageError as e:
                self._us_error(e)

    def delete_user(self):
        """Delete a user."""

        # Get the data from the user.
        vuac = _ViewUserAccount(user_db=self)
        view = _DeleteUserAccountView()
        handler = _UserAccountHandler()

        if vuac.edit_traits(view=view, handler=handler).result:
            # Make absolutely sure.
            name = vuac.name.strip()

            if confirm(None, "Are you sure you want to delete the user \"%s\"?" % name) == YES:
                # Delete the data from the database.
                try:
                    self.user_storage.delete_user(name)
                except UserStorageError as e:
                    self._us_error(e)

    def matching_user(self, name):
        """Select a user."""

        name, description = self._select_user(name)
        if not name:
            return None

        return User(name=name, description=description)

    def user_factory(self):
        """Create a new user object."""

        user = User(name=os.environ.get('USER', ''))

        # Monitor when the blob changes.
        user.on_trait_change(self._blob_changed, name='blob')

        return user

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _get_can_change_password(self):
        """See if a user can change their password."""

        return 'user_password' in self.user_storage.capabilities

    def _get_can_add_user(self):
        """See if a user can be added."""

        return 'user_add' in self.user_storage.capabilities

    def _get_can_modify_user(self):
        """See if a user can be modified."""

        return 'user_modify' in self.user_storage.capabilities

    def _get_can_delete_user(self):
        """See if a user can be deleted."""

        return 'user_delete' in self.user_storage.capabilities

    def _user_storage_default(self):
        """Return the default storage for the user data."""

        # Defer to an external storage manager if there is one.
        try:
            from apptools.permissions.external.user_storage import UserStorage
        except ImportError:
            from apptools.permissions.default.user_storage import UserStorage

        return UserStorage()

    def _blob_changed(self, user, tname, old, new):
        """Invoked when the user's blob data changes."""

        if not self._updating_blob_internally:
            try:
                self.user_storage.update_blob(user.name, user.blob)
            except UserStorageError as e:
                self._us_error(e)

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _select_user(self, name):
        """Select a user returning the data as a tuple of name and description.
        """

        # Get all users that satisfy the criteria.
        try:
            users = self.user_storage.matching_users(name)
        except UserStorageError as e:
            self._us_error(e)
            return '', ''

        if len(users) == 0:
            error(None, "There is no user that matches \"%s\"." % name)
            return '', ''

        return select_user(users)

    @staticmethod
    def _us_error(e):
        """Display a message to the user after a UserStorageError exception has
        been raised.  If the message is empty then we assume the user has
        already been informed."""

        msg = str(e)
        if msg:
            error(None, msg)


def _validate_password(password, confirmation):
    """Validate a password and return True if it is valid."""

    MIN_PASSWORD_LEN = 6

    if password != confirmation:
        error(None, "The passwords do not match.")
        return False

    if not password:
        error(None, "A password must be given.")
        return False

    if len(password) < MIN_PASSWORD_LEN:
        error(None, "The password must be at least %d characters long." % MIN_PASSWORD_LEN)
        return False

    return True
