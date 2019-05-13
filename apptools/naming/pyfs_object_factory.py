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
""" Object factory for Python File System contexts. """


# Enthought library imports.
from apptools.io.api import File

# Local imports.
from .object_factory import ObjectFactory
from .reference import Reference


class PyFSObjectFactory(ObjectFactory):
    """ Object factory for Python File System contexts. """

    ###########################################################################
    # 'ObjectFactory' interface.
    ###########################################################################

    def get_object_instance(self, state, name, context):
        """ Creates an object using the specified state information. """

        obj = None

        if isinstance(state, Reference):
            if state.class_name == 'File' and  len(state.addresses) > 0:
                obj = File(state.addresses[0].content)

        return obj

### EOF #######################################################################
