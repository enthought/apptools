# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Naming exceptions. """


class NamingError(Exception):
    """Base class for all naming exceptions."""


class InvalidNameError(NamingError):
    """Invalid name.

    This exception is thrown when the name passed to a naming operation does
    not conform to the syntax of the naming system (or is empty etc).

    """


class NameAlreadyBoundError(NamingError):
    """Name already bound.

    This exception is thrown when an attempt is made to bind a name that is
    already bound in the current context.

    """


class NameNotFoundError(NamingError):
    """Name not found.

    This exception is thrown when a component of a name cannot be resolved
    because it is not bound in the current context.

    """


class NotContextError(NamingError):
    """Not a context.

    This exception is thrown when a naming operation has reached a point where
    a context is required to continue the operation, but the resolved object
    is not a context.

    """


class OperationNotSupportedError(NamingError):
    """The context does support the requested operation."""
