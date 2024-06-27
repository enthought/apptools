# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" The event fired by the tree model when it changes. """


# Enthought library imports.
from traits.api import HasTraits, Instance

# Local imports.
from .binding import Binding


# Classes for event traits.
class NamingEvent(HasTraits):
    """ Information about tree model changes. """

    # The old binding.
    old_binding = Instance(Binding)

    # The new binding.
    new_binding = Instance(Binding)
