#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Enthought, Inc.
# Description: <Enthought naming package component>
#------------------------------------------------------------------------------
""" The base class for all state factories. """


# Enthought library imports.
from traits.api import HasPrivateTraits


class StateFactory(HasPrivateTraits):
    """ The base class for all state factories.

    A state factory accepts an object and returns some data representing the
    object that is suitable for storing in a particular context.

    """

    ###########################################################################
    # 'StateFactory' interface.
    ###########################################################################

    def get_state_to_bind(self, obj, name, context):
        """ Returns the state of an object for binding.

        Returns None if the factory cannot create the state (ie. it does not
        recognise the object passed to it).

        """

        raise NotImplementedError

### EOF #######################################################################
