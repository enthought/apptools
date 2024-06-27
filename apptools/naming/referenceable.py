# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Base class for classes that can produce a reference to themselves. """


# Enthought library imports.
from traits.api import HasPrivateTraits, Instance

# Local imports.
from .reference import Reference


class Referenceable(HasPrivateTraits):
    """ Base class for classes that can produce a reference to themselves. """

    #### 'Referenceable' interface ############################################

    # The object's reference suitable for binding in a naming context.
    reference = Instance(Reference)
