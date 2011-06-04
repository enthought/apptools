""" The help code interface.

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


from traits.api import Interface, File, Str

class IHelpCode(Interface):
    """ The interface for help code.

    A help code is defined by a UI label and a filename.
    """

    # The UI label for the demo, which appears in menus or dialogs.
    label = Str

    # The path to the file containing the code entry point. This may be
    # absolute, or relative to the Python directory (sys.prefix).
    filename = File

    # The unique ID of the preferences node that contains the other values for
    # this object
    preferences_path = Str

    # The code to execute. This is executed when filename is None or an empty
    # string.
    code = Str
