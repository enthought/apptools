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
from enthought.traits.api import Bool, HasTraits, implements, Instance, Int, \
        Password, Str, Unicode
from enthought.traits.ui.api import Handler, Item, View
from enthought.traits.ui.menu import Action, OKCancelButtons

# Local imports.
from enthought.permissions.i_user import IUser
from i_user_database import IUserDatabase


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
    user_db = Instance('AbstractUserDatabase')


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

        # Get the user name.
        vuac = self._user_account(info)
        name = vuac.name.strip()

        if name:
            try:
                self.search(vuac, name)
            except UserDatabaseError, e:
                self.error(str(e))
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

        if not vuac.name.strip():
            self.error("A user name must be given.")
            return False

        if not _validate_password(vuac.password, vuac.confirm_password):
            return False

        return True

    def search(self, vuac, name):
        """Search the user database to see if a user already exists."""

        # See if there is a user with the name.
        if vuac.user_db.db_user_exists(name):
            self.error("A user called \"%s\" already exists." % name)
        else:
            self.inform("A user called \"%s\" doesn't currently exist." % name)


class _ModifyUserAccountHandler(_AddUserAccountHandler):
    """The traits handler for the modify user account view that validates the
    data."""

    ###########################################################################
    # '_UserAccountHandler' interface.
    ###########################################################################

    def search(self, vuac, name):
        """Search the user database and update the viewed object appropriately.
        """

        full_name, description, password = vuac.user_db.db_search_user(name)

        if full_name is None:
            if name:
                self.error("There is no user whose name starts with \"%s\"." % name)
            else:
                self.error("No users have been defined.")
        else:
            # Update the viewed object.
            vuac.name = full_name
            vuac.description = description
            vuac.password = vuac.confirm_password = password


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


class User(HasTraits):
    """The user implementation.  We don't store any extra information other
    than that defined by IUser."""

    implements(IUser)

    #### 'IUser' interface ####################################################

    name = Unicode

    authenticated = Bool(False)

    description = Unicode

    blob = Str


class UserDatabaseError(Exception):
    """This is the exception raised by an AbstractUserDatabase subclass when an
    error occurs accessing the database.  Its string representation is
    displayed as an error message to the user."""


class AbstractUserDatabase(HasTraits):
    """This implements a user database that supports IUser for the default user
    manager (ie. using password authorisation) except that it leaves the actual
    access of the data to a subclass."""

    implements(IUserDatabase)

    #### 'IUserDatabase' interface ############################################

    can_change_password = True

    can_add_user = True

    can_modify_user = True

    can_delete_user = True

    #### Private interface ####################################################

    # The saved result of whether or not the database is empty.
    _bootstrap = Int(-1)

    # Set if updating the user blob internally.
    _updating_blob_internally = Bool(False)

    ###########################################################################
    # 'IUserDatabase' interface.
    ###########################################################################

    def bootstrapping(self):
        """See if we are bootstrapping."""

        # This might be called often so we only check once and save the result.
        if self._bootstrap < 0:
            try:
                self._bootstrap = int(self.db_is_empty())
            except UserDatabaseError:
                # Suppress the error and assume it isn't empty.
                self._bootstrap = 0

        return (self._bootstrap > 0)

    def authenticate_user(self, user):
        """Authenticate a user."""

        # Get the login details.
        name = user.name
        lu = _LoginUser(name=name)

        if not lu.edit_traits().result:
            return False

        # Get the user account and compare passwords.
        try:
            name, description, blob, password = self.db_get_user(lu.name.strip())
        except UserDatabaseError, e:
            self._db_error(e)
            return False

        if name is None or password != lu.password:
            # It's bad security to give too much information...
            error(None, "The user name or password is invalid.")
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

        # There is nothing to do to unauthenticate so it is always successful.
        return True

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
            self.db_update_password(name, np.new_password)
        except UserDatabaseError, e:
            self._db_error(e)

    def add_user(self):
        """Add a user."""

        # Get the data from the user.
        vuac = _ViewUserAccount(user_db=self)
        view = _AddUserAccountView()
        handler = _AddUserAccountHandler()

        if vuac.edit_traits(view=view, handler=handler).result:
            # Add the data to the database.
            try:
                self.db_add_user(vuac.name.strip(), vuac.description,
                        vuac.password)
            except UserDatabaseError, e:
                self._db_error(e)

    def modify_user(self):
        """Modify a user."""

        # Get the data from the user.
        vuac = _ViewUserAccount(user_db=self)
        view = _ModifyUserAccountView()
        handler = _ModifyUserAccountHandler()

        if vuac.edit_traits(view=view, handler=handler).result:
            # Update the data in the database.
            try:
                self.db_update_user(vuac.name.strip(), vuac.description,
                        vuac.password)
            except UserDatabaseError, e:
                self._db_error(e)

    def delete_user(self):
        """Delete a user."""

        # Get the data from the user.
        vuac = _ViewUserAccount(user_db=self)
        view = _DeleteUserAccountView()
        handler = _DeleteUserAccountHandler()

        if vuac.edit_traits(view=view, handler=handler).result:
            # Make absolutely sure.
            name = vuac.name.strip()

            if confirm(None, "Are you sure you want to delete the user \"%s\"?" % name) == YES:
                # Delete the data from the database.
                try:
                    self.db_delete_user(name)
                except UserDatabaseError, e:
                    self._db_error(e)

    def user_factory(self):
        """Create a new user object."""

        user = User(name=os.environ.get('USER', ''), _user_db=self)

        # Monitor when the blob changes.
        user.on_trait_change(self._blob_changed, name='blob')

        return user

    ###########################################################################
    # 'AbstractUserDatabase' interface.
    ###########################################################################

    def db_add_user(self, name, description, password):
        """This must be reimplemented to add a new user with the given name,
        description and password."""

        raise NotImplementedError

    def db_delete_user(self, name):
        """This must be reimplemented to delete the user with the given name
        (which will not be empty)."""

        raise NotImplementedError

    def db_is_empty(self):
        """This must be reimplemented to return True if the user database is
        empty.  It will only ever be called once."""

        raise NotImplementedError

    def db_get_user(self, name):
        """This must be reimplemented to return a tuple of the name,
        description, blob and password of the user with the given name."""

        raise NotImplementedError

    def db_search_user(self, name):
        """This must be reimplemented to return a tuple of the full name,
        description and password of the user with either the given name, or
        the first user whose name starts with the given name."""

        raise NotImplementedError

    def db_update_blob(self, name, blob):
        """This must be reimplemented to update the blob for the user with the
        given name (which will not be empty)."""

        raise NotImplementedError

    def db_update_password(self, name, password):
        """This must be reimplemented to update the password for the user with
        the given name (which will not be empty)."""

        raise NotImplementedError

    def db_update_user(self, name, description, password):
        """This must be reimplemented to update the description and password
        for the user with the given name (which will not be empty)."""

        raise NotImplementedError

    def db_user_exists(self, name):
        """This must be reimplemented to return True if a user with the given
        name (which will not be empty) exists in the user database."""

        raise NotImplementedError

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _blob_changed(self, user, tname, old, new):
        """Invoked when the user's blob data changes."""

        if not self._updating_blob_internally:
            try:
                self.db_update_blob(user.name, user.blob)
            except UserDatabaseError, e:
                self._db_error(e)

    ###########################################################################
    # Private interface.
    ###########################################################################

    @staticmethod
    def _db_error(e):
        """Display a message to the user after a UserDatabaseError exception
        has been raised."""

        error(None, str(e))


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
