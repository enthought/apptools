# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
import logging

from apptools.preferences.api import PreferencesHelper
from traits.api import Bool, Str, Trait


class LoggerPreferences(PreferencesHelper):
    """The persistent service exposing the Logger plugin's API."""

    #### Preferences ##########################################################

    # The log levels
    level = Trait(
        "Info",
        {
            "Debug": logging.DEBUG,
            "Info": logging.INFO,
            "Warning": logging.WARNING,
            "Error": logging.ERROR,
            "Critical": logging.CRITICAL,
        },
        is_str=True,
    )

    enable_agent = Bool(False)
    smtp_server = Str()
    to_address = Str()
    from_address = Str()

    # The path to the preferences node that contains the preferences.
    preferences_path = Str("apptools.logger")
