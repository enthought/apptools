""" The help doc interface.

    :Copyright: 2008, Enthought Inc.
    :License: BSD
    :Author: Janet Swisher
"""
# This software is provided without warranty under the terms of the BSD
# license included in AppTools/trunk/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!

from traits.api import Interface, Either, File, Str, Bool

class IHelpDoc(Interface):
    """ The interface for help docs.

    A help doc is defined by a UI label, a filename, and a viewer program.
    """

    # The UI label for the help doc, which appears in menus or dialogs.
    label = Str

    # The path to the document, which can be full, or relative to the Python
    # installation directory (sys.prefix).
    filename = File

    # Is this a url?
    url = Bool(False)

    # The program to use to view the document. 'browser' means the platform
    # default web browser. Otherwise, it is a command to run, which may be
    # in the program search path of the current environment, or an absolute
    # path to a program.
    viewer = Either('browser', Str)

    # The unique ID of the preferences node that contains the other values for
    # this object
    preferences_path = Str
