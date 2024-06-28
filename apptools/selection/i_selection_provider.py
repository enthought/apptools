# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
from traits.api import Event, Interface, Str


class ISelectionProvider(Interface):
    """ Source of selections. """

    #: Unique ID identifying the provider.
    provider_id = Str()

    #: Event triggered when the selection changes.
    #: The content of the event is an :class:`~.ISelection` instance.
    selection = Event

    def get_selection(self):
        """Return the current selection.

        Returns:
            selection -- ISelection
                Object representing the current selection.
        """

    def set_selection(self, items, ignore_missing=False):
        """Set the current selection to the given items.

        If ``ignore_missing`` is ``True``, items that are not available in the
        selection provider are silently ignored. If it is ``False`` (default),
        an :class:`~.ValueError` should be raised.

        Arguments:
            items -- list
                List of items to be selected.

            ignore_missing -- bool
                If ``False`` (default), the provider raises an exception if any
                of the items in ``items`` is not available to be selected.
                Otherwise, missing elements are silently ignored, and the rest
                is selected.
        """
