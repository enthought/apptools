""" The help code implementation.

    This may be used to define examples to be displayed or demos to be run.

    :Copyright: 2008, Enthought Inc.
    :License: BSD
    :Author: Janet Swisher
"""
# This software is provided without warranty under the terms of the BSD
# license included in AppTools/trunk/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!

from traits.api import File, Str, provides

from apptools.preferences.api import PreferencesHelper
from .i_help_code import IHelpCode


@provides(IHelpCode)
class HelpCode(PreferencesHelper):
    """ The implementation for help codes.

    A help code is defined by a UI label and a filename.
    """


    #### IHelpCode interface / Preferences #####################################

    # NOTE: This class inherits preferences_page from PreferencesHelper.

    # The UI label for the help code, which appears in menus or dialogs.
    label = Str

    # The path to the entry point, which can be full, or relative to the Python
    # installation directory (sys.prefix).
    filename = File

    # The code to execute. This is executed when filename is None or an empty
    # string.
    code = Str

