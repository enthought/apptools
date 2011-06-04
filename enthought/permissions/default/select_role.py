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


class _Role(HasTraits):
    """This represents the role model."""

    #### '_RoleModel' interface ###############################################

    # The role name.
    name = Unicode

    # The role description.
    description = Unicode

    # The permissions ids.
    permissions = List


class _RolesView(HasTraits):
    """This represents the view used to select a role."""

    #### '_UsersView' interface ###############################################

    # The list of roles to select from.
    model = List(_Role)

    # The selected user.
    selection = Instance(_Role)

    # The editor used by the view.
    table_editor = TableEditor(columns=[ObjectColumn(name='name'),
                    ObjectColumn(name='description')],
            selected='selection', sort_model=True, configurable=False)

    # The default view.
    traits_view = View(Item('model', show_label=False, editor=table_editor),
            title="Select a Role", style='readonly', kind='modal',
            buttons=OKCancelButtons)


def select_role(roles):
    """Return a single role from the given list of roles."""

    # Construct the model.
    model = [_Role(name=name, description=description, permissions=permissions)
            for name, description, permissions in roles]

    # Construct the view.
    view = _RolesView(model=model)

    if view.configure_traits() and view.selection is not None:
        role = view.selection.name, view.selection.description, view.selection.permissions
    else:
        role = '', '', []

    return role
