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
from enthought.pyface.api import confirm, error, YES
from enthought.traits.api import HasTraits, Instance, List, Unicode
from enthought.traits.ui.api import Group, Handler, Item, SetEditor, View
from enthought.traits.ui.menu import Action, CancelButton

# Local imports.
from enthought.permissions.i_policy_manager import IPolicyManager
from enthought.permissions.permission import Permission
from i_policy_storage import PolicyStorageError


class _Role(HasTraits):
    """This represents a role."""

    # The role name.
    name = Unicode

    # The role description.
    description = Unicode

    # The permissions that define the role.
    permissions = List(Instance(Permission))

    def __str__(self):
        """Return a user friendly representation."""

        s = self.description
        if not s:
            s = self.name

        return s


class _Assignment(HasTraits):
    """This represents the assignment of roles to a user."""

    # The user name.
    user_name = Unicode

    # The list of assigned roles.
    roles = List(Instance(_Role))


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

        perms_editor = SetEditor(values=policy.permissions.values(),
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

    pm = Instance(IPolicyManager)

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _search_clicked(self, info):
        """Invoked by the "Search" button."""

        role = self._validate(info)
        if role is None:
            return

        full_name, description, perm_names = self.pm.policy_storage.search_role(role.name)
        if full_name is None:
            self._error("There is no role whose name starts with \"%s\"." % role.name)
            return

        # Update the viewed object.
        role.name = full_name
        role.description = description
        role.permissions = self._perms_to_list(perm_names)

    def _add_clicked(self, info):
        """Invoked by the "Add" button."""

        role = self._validate(info)
        if role is None:
            return

        # Add the data to the database.
        try:
            self.pm.policy_storage.add_role(role.name, role.description,
                    [p.name for p in role.permissions])
            info.ui.dispose()
        except PolicyStorageError, e:
            self._ps_error(e)

    def _modify_clicked(self, info):
        """Invoked by the "Modify" button."""

        role = self._validate(info)
        if role is None:
            return

        # Update the data in the database.
        try:
            self.pm.policy_storage.update_role(role.name, role.description,
                    [p.name for p in role.permissions])
            info.ui.dispose()
        except PolicyStorageError, e:
            self._ps_error(e)

    def _delete_clicked(self, info):
        """Invoked by the "Delete" button."""

        role = self._validate(info)
        if role is None:
            return

        if confirm(None, "Are you sure you want to delete the role \"%s\"?" % role.name) == YES:
            # Delete the data from the database.
            try:
                self.pm.policy_storage.delete_role(role.name)
                info.ui.dispose()
            except PolicyStorageError, e:
                self._ps_error(e)

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _validate(self, info):
        """Validate the role and return the it if there were no problems."""

        role = self._role(info)
        role.name = role.name.strip()

        if not role.name:
            self._error("A role name must be given.")
            return None

        return role

    def _perms_to_list(self, perm_names):
        """Return a list of Permission instances created from the given list of
        permission names."""

        pl = []

        for name in perm_names:
            try:
                p = self.pm.permissions[name]
            except KeyError:
                # FIXME: permissions should be populated from the policy
                # database - or is it needed at all?  Should it just be read
                # when managing roles?
                p = Permission(name=name, application_defined=False)

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


def role_definition(policy_manager):
    """Implement the role definition for the given policy manager."""

    role = _Role()
    view = _RoleView(policy_manager)
    handler = _RoleHandler(pm=policy_manager)

    role.edit_traits(view=view, handler=handler)
