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

from .adapter_base import AdapterBase
from .i_policy_manager import IPolicyManager
from .i_user import IUser
from .i_user_manager import IUserManager
from .package_globals import get_permissions_manager, set_permissions_manager
from .permission import ManagePolicyPermission, ManageUsersPermission, Permission
from .permissions_manager import PermissionsManager
from .secure_proxy import SecureHandler, SecureProxy
