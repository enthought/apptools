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
from traits.api import Bool, Dict, Interface, Unicode


class IUser(Interface):
    """The interface implemented by a user (or principal)."""

    # The user's name, ie. how they identified themselves to the permissions
    # policy.  It is only valid if the authenticated trait is True.
    name = Unicode

    # This is set if the user has been authenticated, ie. the name trait is
    # valid.
    authenticated = Bool(False)

    # An optional description of the user (eg. their full name).  The exact
    # meaning is defined by the user manager.
    description = Unicode

    # This allows application defined, user specific data to be persisted in
    # the user database.  An application (or plugin) should save the data as a
    # single value in the dictionary keyed on the application's (or plugin's)
    # unique id.  The data will be saved in the user database whenever it is
    # changed, and will be read from the user database whenever the user is
    # authenticated.
    blob = Dict

    def __str__(self):
        """Return a user friendly representation of the user."""
