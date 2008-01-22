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
from enthought.pyface.api import confirm, error, information, YES
from enthought.traits.api import Instance
from enthought.traits.ui.api import Group, Handler, Item, SetEditor, View
from enthought.traits.ui.menu import Action, CancelButton

# Local imports.
from enthought.permissions.i_permissions_policy import IPermissionsPolicy
from policy_data import Role


class _RoleView(View):
    """The view for handling roles."""

    #### 'View' interface #####################################################

    kind = 'modal'

    title = "Define roles"

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, policy, **traits):
        """Initialise the object."""

        buttons = [Action(name="Search"), Action(name="Add"),
                Action(name="Modify"), Action(name="Delete"), CancelButton]

        perms_editor = SetEditor(values=policy.perms,
                left_column_title="Available Permissions",
                right_column_title="Assigned Permissions")

        perms_group = Group(Item(name='permissions', editor=perms_editor),
                label='Permissions', show_border=True, show_labels=False)

        super(_RoleView, self).__init__(Item(name='name'),
                Item(name='description'), perms_group, buttons=buttons,
                **traits)


class _RoleHandler(Handler):
    """The view handler for roles."""

    #### Private interface ####################################################

    policy = Instance(IPermissionsPolicy)

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _search_clicked(self, info):
        """Invoked by the "Search" button."""

        print "Search"

    def _add_clicked(self, info):
        """Invoked by the "Add" button."""

        print "Add"

    def _modify_clicked(self, info):
        """Invoked by the "Modify" button."""

        print "Modify"

    def _delete_clicked(self, info):
        """Invoked by the "Delete" button."""

        print "Delete"


def role_definition(policy):
    """Implement the role definition for the given permissions policy."""

    role = Role()
    view = _RoleView(policy=policy)
    handler = _RoleHandler(policy=policy)

    role.edit_traits(view=view, handler=handler)
