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
""" The address of a commuications endpoint. """


# Enthought library imports.
from traits.api import Any, HasTraits, Str


class Address(HasTraits):
    """ The address of a communications end-point.

    It contains a type that describes the communication mechanism, and the
    actual address content.

    """

    # The type of the address.
    type = Str

    # The actual content.
    content = Any

#### EOF ######################################################################
