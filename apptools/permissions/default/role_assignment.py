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
from pyface.api import error
from traits.api import Dict, Instance
from traitsui.api import Group, Handler, Item, SetEditor, View
from traitsui.menu import Action, CancelButton

# Local imports.
from apptools.permissions.package_globals import get_permissions_manager
from .i_policy_storage import PolicyStorageError
from .policy_data import Assignment, Role


class _AssignmentView(View):
    """The view for handling role assignments."""

    #### 'View' interface #####################################################

    kind = 'modal'

    title = "Assign roles"

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, all_roles, **traits):
        """Initialise the object."""

        buttons = [Action(name="Search"), Action(name="Save"), CancelButton]

        roles_editor = SetEditor(values=list(all_roles.values()),
                left_column_title="Available Roles",
                right_column_title="Assigned Roles")

        roles_group = Group(Item(name='roles', editor=roles_editor),
                label='Roles', show_border=True, show_labels=False)

        super(_AssignmentView, self).__init__(Item(name='user_name'),
                Item(name='description', style='readonly'), roles_group,
                buttons=buttons, **traits)


class _AssignmentHandler(Handler):
    """The view handler for role assignments."""

    #### Private interface ####################################################

    all_roles = Dict

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _search_clicked(self, info):
        """Invoked by the "Search" button."""

        pm = get_permissions_manager()
        assignment = self._assignment(info)

        user = pm.user_manager.matching_user(assignment.user_name)
        if user is None:
            return

        try:
            user_name, role_names = pm.policy_manager.policy_storage.get_assignment(user.name)
        except PolicyStorageError as e:
            self._ps_error(e)
            return

        # Update the viewed object.
        assignment.user_name = user.name
        assignment.description = user.description
        assignment.roles = self._roles_to_list(role_names)

    def _save_clicked(self, info):
        """Invoked by the "Save" button."""

        assignment = self._validate(info)
        if assignment is None:
            return

        # Update the data in the database.
        try:
            get_permissions_manager().policy_manager.policy_storage.set_assignment(assignment.user_name, [r.name for r in assignment.roles])

            info.ui.dispose()
        except PolicyStorageError as e:
            self._ps_error(e)

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _validate(self, info):
        """Validate the assignment and return it if there were no problems."""

        assignment = self._assignment(info)
        assignment.user_name = assignment.user_name.strip()

        if not assignment.user_name:
            self._error("A user name must be given.")
            return None

        return assignment

    def _roles_to_list(self, role_names):
        """Return a list of Role instances created from the given list of role
        names."""

        rl = []

        for name in role_names:
            try:
                r = self.all_roles[name]
            except KeyError:
                # This shouldn't happen if the policy database is maintaining
                # referential integrity.
                continue

            rl.append(r)

        return rl

    @staticmethod
    def _assignment(info):
        """Return the assignment instance being handled."""

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


def role_assignment():
    """Implement the role assignment for the current policy manager."""

    # Create a dictionary of roles keyed by the role name.
    all_roles = {}

    try:
        roles = get_permissions_manager().policy_manager.policy_storage.all_roles()
    except PolicyStorageError as e:
        error(None, str(e))
        return

    for name, description in roles:
        all_roles[name] = Role(name=name, description=description)

    assignment = Assignment()
    view = _AssignmentView(all_roles)
    handler = _AssignmentHandler(all_roles=all_roles)

    assignment.edit_traits(view=view, handler=handler)
