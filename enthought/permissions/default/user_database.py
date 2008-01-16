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
from enthought.pyface.api import error
from enthought.traits.api import Dict, HasTraits, implements, Instance, \
        Password, Unicode
from enthought.traits.ui.api import Handler, Item, View
from enthought.traits.ui.menu import OKCancelButtons

# Local imports.
from i_user_database import IUserDatabase
from persistent import Persistent, PersistentError


class UserAccount(HasTraits):
    """This represents a single account in the persisted user database."""

    # The name the user uses to identify themselves.
    name = Unicode

    # A description of the user (typically their full name).
    description = Unicode

    # The user's password.
    password = Unicode


class UserDb(HasTraits):
    """This is the persisted user database."""

    # The dictionary of user accounts.
    users = Dict


class _UserAccount(UserAccount):
    """This represents a single account when edited."""

    # The password
    password = Password

    # The password confirmation.
    confirm_password = Password


class _UserAccountHandler(Handler):
    """The traits handler for the user account view that validates the data."""

    MIN_PASSWORD_LEN = 6

    def close(self, info, is_ok):
        """Reimplemented to validate the data."""

        # If the user cancelled then close the dialog.
        if not is_ok:
            return True

        # Validate the form.
        return self.validate(info.ui.context['object'])

    def validate(self, uac):
        """Actually do the validation of the given object and return True if
        there were no problems."""

        if not uac.name.strip():
            self.error("A user name must be given.")
            return False

        if uac.password != uac.confirm_password:
            self.error("The passwords do not match.")
            return False

        if not uac.password:
            self.error("A password must be given.")
            return False

        if len(uac.password) < self.MIN_PASSWORD_LEN:
            self.error("The password must be at least %d characters long." % self.MIN_PASSWORD_LEN)
            return False

        return True

    def error(self, msg):
        """Display an error message to the user."""

        error(None, msg)


def _UserAccountView(title):
    """Create a view to handle a user account."""

    return View(Item(name='name'), Item(name='description'),
            Item(name='password'), Item(name='confirm_password'), title=title,
            kind='modal', buttons=OKCancelButtons,
            handler=_UserAccountHandler())


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
        """TODO"""

        # Always authenticate for the moment.
        return True

    def unauthenticate_user(self, user):

        # There is nothing to do to unauthenticate so it is always successful.
        return True

    def add_user(self):

        # Get the data from the user.
        vuac = _UserAccount()
        view = _UserAccountView("Add a user")

        if vuac.edit_traits(view=view).result:
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
        """TODO"""

        from enthought.pyface.api import information

        information(None, "This will eventually implement a TraitsUI based GUI for modifying users.")

    def delete_user(self):
        """TODO"""

        from enthought.pyface.api import information

        information(None, "This will eventually implement a TraitsUI based GUI for deleting users.")

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def __db_default(self):
        """Return the default persisted database."""

        return Persistent(UserDb, 'ets_perms_userdb', "the user database")
