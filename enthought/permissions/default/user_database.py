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
from enthought.traits.api import Dict, HasTraits, implements, Instance

# Local imports.
from i_user_database import IUserDatabase
from persistent import Persistent
from user_account import UserAccount


class _Db(Persistent):
    """This is the persisted user database."""

    # The dictionary of user accounts.
    users = Dict


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
    _db = Instance(_Db)

    ###########################################################################
    # 'IUserDatabase' interface.
    ###########################################################################

    def add_user(self):
        """TODO"""

        from enthought.pyface.api import information

        information(None, "This will eventually implement a TraitsUI based GUI for adding users.")

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
        """Return the default persisted data."""

        return _Db('ets_perms_userdb', 'ETS_PERMS_USERDB')
