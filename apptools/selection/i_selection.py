# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
from traits.api import Interface, List, Str


class ISelection(Interface):
    """ Collection of selected items. """

    #: ID of the selection provider that created this selection object.
    provider_id = Str

    def is_empty(self):
        """ Is the selection empty? """


class IListSelection(ISelection):
    """ Selection for ordered sequences of items. """

    #: Selected objects.
    items = List

    #: Indices of the selected objects in the selection provider.
    indices = List
