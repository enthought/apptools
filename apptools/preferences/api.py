# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" API for apptools.preferences subpackage.

- :class:`~.Preferences`
- :class:`~.PreferenceBinding`
- :class:`~.PreferencesHelper`
- :class:`~.ScopedPreferences`

Interfaces
----------
- :class:`~.IPreferences`

Utilities
---------

- :func:`~.get_default_preferences`
- :func:`~.set_default_preferences`
- :func:`~.bind_preference`
"""

from .i_preferences import IPreferences

from .package_globals import get_default_preferences, set_default_preferences
from .preferences import Preferences
from .preference_binding import PreferenceBinding, bind_preference
from .preferences_helper import PreferencesHelper
from .scoped_preferences import ScopedPreferences
