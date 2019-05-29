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
""" The base class for all context adapters. """


# Enthought library imports.
from traits.api import Any, Dict, Instance, Property, Str

# Local imports.
from .context import Context


class ContextAdapter(Context):
    """ The base class for all context adapters. """

    #### 'ContextAdapter' interface ###########################################

    # The object that we are adapting.
    adaptee = Any

    # The context that the object is in.
    context = Instance(Context)

#### EOF ######################################################################
