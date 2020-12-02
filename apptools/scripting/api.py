# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
"""Public API for the scripting package.
"""

from .recorder import Recorder, RecorderError
from .recordable import recordable
from .package_globals import get_recorder, set_recorder
from .recorder_with_ui import RecorderWithUI
from .util import start_recording, stop_recording
