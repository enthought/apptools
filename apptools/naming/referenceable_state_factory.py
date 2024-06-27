# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" State factory for referenceable objects. """


# Local imports.
from .referenceable import Referenceable
from .state_factory import StateFactory


class ReferenceableStateFactory(StateFactory):
    """ State factory for referenceable objects. """

    ###########################################################################
    # 'StateFactory' interface.
    ###########################################################################

    def get_state_to_bind(self, obj, name, context):
        """ Returns the state of an object for binding. """

        state = None

        # If the object knows how to create a reference to it then let it
        # do so.
        if isinstance(obj, Referenceable):
            state = obj.reference

        return state
