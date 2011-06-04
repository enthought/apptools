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
""" The base class for all object factories. """


# Enthought library imports.
from traits.api import HasTraits


class ObjectFactory(HasTraits):
    """ The base class for all object factories.

    An object factory accepts some information about how to create an object
    (such as a reference) and returns an instance of that object.

    """

    ###########################################################################
    # 'ObjectFactory' interface.
    ###########################################################################

    def get_object_instance(self, state, name, context):
        """ Creates an object using the specified state information.

        Returns None if the factory cannot create the object (ie. it does not
        recognise the state passed to it).

        """

        raise NotImplementedError

### EOF #######################################################################
