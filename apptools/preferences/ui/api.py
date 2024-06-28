# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" API for the apptools.preferences.ui subpackage.

- :class:`~.IPreferencesPage`
- :class:`~.PreferencesManager`
- :class:`~.PreferencesPage`
"""

from .i_preferences_page import IPreferencesPage

from .preferences_manager import PreferencesManager
from .preferences_page import PreferencesPage
