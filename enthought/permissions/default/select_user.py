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
from traits.api import HasTraits, Instance, List, Unicode
from traitsui.api import Item, TableEditor, View
from traitsui.menu import OKCancelButtons
from traitsui.table_column import ObjectColumn


class _User(HasTraits):
    """This represents the user model."""

    #### '_User' interface ####################################################

    # The user name.
    name = Unicode

    # The user description.
    description = Unicode


class _UsersView(HasTraits):
    """This represents the view used to select a user."""

    #### '_UsersView' interface ###############################################

    # The list of users to select from.
    model = List(_User)

    # The selected user.
    selection = Instance(_User)

    # The editor used by the view.
    table_editor = TableEditor(columns=[ObjectColumn(name='name'),
                    ObjectColumn(name='description')],
            selected='selection', sort_model=True, configurable=False)

    # The default view.
    traits_view = View(Item('model', show_label=False, editor=table_editor),
            title="Select a User", style='readonly', kind='modal',
            buttons=OKCancelButtons)


def select_user(users):
    """Return a single user from the given list of users."""

    # Construct the model.
    model = [_User(name=name, description=description)
            for name, description in users]

    # Construct the view.
    view = _UsersView(model=model)

    if view.configure_traits() and view.selection is not None:
        user = view.selection.name, view.selection.description
    else:
        user = '', ''

    return user
