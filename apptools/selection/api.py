# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" API for the apptools.selection subpackage.

- :class:`~.ListSelection`
- :class:`~.SelectionService`

Interfaces
----------
- :class:`~.ISelection`
- :class:`~.IListSelection`
- :class:`~.ISelectionProvider`

Custom Exceptions
-----------------
- :class:`~.IDConflictError`
- :class:`~.ListenerNotConnectedError`
- :class:`~.ProviderNotRegisteredError`
"""

from .errors import (
    IDConflictError,
    ListenerNotConnectedError,
    ProviderNotRegisteredError,
)
from .i_selection import ISelection, IListSelection
from .i_selection_provider import ISelectionProvider
from .list_selection import ListSelection
from .selection_service import SelectionService
