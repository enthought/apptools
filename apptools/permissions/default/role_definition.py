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
from pyface.api import confirm, error, YES
from traits.api import Instance
from traitsui.api import Group, Handler, Item, SetEditor, View
from traitsui.menu import Action, CancelButton

# Local imports.
from apptools.permissions.package_globals import get_permissions_manager
from apptools.permissions.permission import Permission
from .i_policy_storage import PolicyStorageError
from .policy_data import Role
from .select_role import select_role


class _RoleView(View):
    """The view for handling roles."""

    #### 'View' interface #####################################################

    kind = 'modal'

    title = "Define roles"

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **traits):
        """Initialise the object."""

        buttons = [Action(name="Search"), Action(name="Add"),
                Action(name="Modify"), Action(name="Delete"), CancelButton]

        all_perms = list(get_permissions_manager().policy_manager.permissions.values())

        perms_editor = SetEditor(values=all_perms,
                left_column_title="Available Permissions",
                right_column_title="Assigned Permissions")

        perms_group = Group(Item(name='permissions', editor=perms_editor),
                label='Permissions', show_border=True, show_labels=False)

        super(_RoleView, self).__init__(Item(name='name'),
                Item(name='description'), perms_group, buttons=buttons,
                **traits)


class _RoleHandler(Handler):
    """The view handler for roles."""

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _search_clicked(self, info):
        """Invoked by the "Search" button."""

        role = self._role(info)

        # Get all roles that satisfy the criteria.
        try:
            roles = get_permissions_manager().policy_manager.policy_storage.matching_roles(role.name)
        except PolicyStorageError as e:
            self._ps_error(e)
            return

        if len(roles) == 0:
            self._error("There is no role that matches \"%s\"." % role.name)
            return

        name, description, perm_ids = select_role(roles)

        if name:
            # Update the viewed object.
            role.name = name
            role.description = description
            role.permissions = self._perms_to_list(perm_ids)

    def _add_clicked(self, info):
        """Invoked by the "Add" button."""

        role = self._validate(info)
        if role is None:
            return

        # Add the data to the database.
        try:
            get_permissions_manager().policy_manager.policy_storage.add_role(
                    role.name, role.description,
                    [p.id for p in role.permissions])
            info.ui.dispose()
        except PolicyStorageError as e:
            self._ps_error(e)

    def _modify_clicked(self, info):
        """Invoked by the "Modify" button."""

        role = self._validate(info)
        if role is None:
            return

        # Update the data in the database.
        try:
            get_permissions_manager().policy_manager.policy_storage.modify_role(
                    role.name, role.description,
                    [p.id for p in role.permissions])
            info.ui.dispose()
        except PolicyStorageError as e:
            self._ps_error(e)

    def _delete_clicked(self, info):
        """Invoked by the "Delete" button."""

        role = self._validate(info)
        if role is None:
            return

        if confirm(None, "Are you sure you want to delete the role \"%s\"?" % role.name) == YES:
            # Delete the data from the database.
            try:
                get_permissions_manager().policy_manager.policy_storage.delete_role(role.name)

                info.ui.dispose()
            except PolicyStorageError as e:
                self._ps_error(e)

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _validate(self, info):
        """Validate the role and return it if there were no problems."""

        role = self._role(info)
        role.name = role.name.strip()

        if not role.name:
            self._error("A role name must be given.")
            return None

        return role

    def _perms_to_list(self, perm_ids):
        """Return a list of Permission instances created from the given list of
        permission ids."""

        pl = []

        for id in perm_ids:
            try:
                p = get_permissions_manager().policy_manager.permissions[id]
            except KeyError:
                # FIXME: permissions should be populated from the policy
                # database - or is it needed at all?  Should it just be read
                # when managing roles?
                p = Permission(id=id, application_defined=False)

            pl.append(p)

        return pl

    @staticmethod
    def _role(info):
        """Return the role instance being handled."""

        return info.ui.context['object']

    @staticmethod
    def _error(msg):
        """Display an error message to the user."""

        error(None, msg)

    @staticmethod
    def _ps_error(e):
        """Display a message to the user after a PolicyStorageError exception
        has been raised."""

        error(None, str(e))


def role_definition():
    """Implement the role definition for the current policy manager."""

    role = Role()
    view = _RoleView()
    handler = _RoleHandler()

    role.edit_traits(view=view, handler=handler)
