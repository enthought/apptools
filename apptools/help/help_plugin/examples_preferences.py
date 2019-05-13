""" Preferences for all help examples.

    :Copyright: 2008, Enthought Inc.
    :License: BSD
    :Author: Janet Swisher
"""
# This software is provided without warranty under the terms of the BSD
# license included in AppTools/trunk/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!


from apptools.preferences.api import PreferencesHelper
from traits.api import Either, Enum, File, Str, provides

# This module's package.
PKG = '.'.join(__name__.split('.')[:-1])

class ExamplesPreferences(PreferencesHelper):
    """ Preferences for all help examples.
    """

    #### Preferences ######################################

    # The path to the preferences
    preferences_path = PKG + '.Examples'

    # The external program to use to view the document, if editor_choice is
    # 'external'. It is a command to run, which may be in the program search
    # path of the current environment, or an absolute path to a program.
    editor = Str

