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

#### EOF ######################################################################
