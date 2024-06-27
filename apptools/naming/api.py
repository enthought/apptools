# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" API for the apptools.naming subpackage.

- :class:`~.Address`
- :class:`~.Binding`
- :class:`~.Context`
- :class:`~.DynamicContext`
- :class:`~.DirContext`
- :func:`~.InitialContext`
- :class:`~.InitialContextFactory`
- :class:`~.NamingEvent`
- :attr:`~.naming_manager`
- :class:`~.ObjectFactory`
- :class:`~.ObjectSerializer`
- :class:`~.PyContext`
- :class:`~.PyObjectFactory`
- :class:`~.PyFSContext`
- :class:`~.PyFSContextFactory`
- :class:`~.PyFSInitialContextFactory`
- :class:`~.PyFSObjectFactory`
- :class:`~.PyFSStateFactory`
- :class:`~.Reference`
- :class:`~.Referenceable`
- :class:`~.ReferenceableStateFactory`
- :class:`~.StateFactory`

Custom Exceptions
-----------------

- :class:`~.NamingError`
- :class:`~.InvalidNameError`
- :class:`~.NameAlreadyBoundError`
- :class:`~.NameNotFoundError`
- :class:`~.NotContextError`
- :class:`~.OperationNotSupportedError`
"""

from .exception import NamingError, InvalidNameError, NameAlreadyBoundError
from .exception import NameNotFoundError, NotContextError
from .exception import OperationNotSupportedError

from .address import Address
from .binding import Binding
from .context import Context
from .dynamic_context import DynamicContext
from .dir_context import DirContext
from .initial_context import InitialContext
from .initial_context_factory import InitialContextFactory
from .naming_event import NamingEvent
from .naming_manager import naming_manager
from .object_factory import ObjectFactory
from .object_serializer import ObjectSerializer
from .py_context import PyContext
from .py_object_factory import PyObjectFactory
from .pyfs_context import PyFSContext
from .pyfs_context_factory import PyFSContextFactory
from .pyfs_initial_context_factory import PyFSInitialContextFactory
from .pyfs_object_factory import PyFSObjectFactory
from .pyfs_state_factory import PyFSStateFactory
from .reference import Reference
from .referenceable import Referenceable
from .referenceable_state_factory import ReferenceableStateFactory
from .state_factory import StateFactory
