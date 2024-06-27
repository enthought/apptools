# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" The interface for pages in a preferences dialog. """


# Enthought library imports.
from traits.api import Interface, Str


class IPreferencesPage(Interface):
    """ The interface for pages in a preferences dialog. """

    # The page's category (e.g. 'General/Appearence'). The empty string means
    # that this is a top-level page.
    category = Str

    # The page's help identifier (optional). If a help Id *is* provided then
    # there will be a 'Help' button shown on the preference page.
    help_id = Str

    # The page name (this is what is shown in the preferences dialog).
    name = Str

    def apply(self):
        """ Apply the page's preferences. """
        pass
