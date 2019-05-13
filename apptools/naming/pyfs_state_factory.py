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
""" State factory for Python File System contexts. """


# Enthought library imports.
from apptools.io.api import File

# Local imports.
from .address import Address
from .reference import Reference
from .state_factory import StateFactory


class PyFSStateFactory(StateFactory):
    """ State factory for Python File System contexts. """

    ###########################################################################
    # 'StateFactory' interface.
    ###########################################################################

    def get_state_to_bind(self, obj, name, context):
        """ Returns the state of an object for binding. """

        state = None

        if isinstance(obj, File):
            # If the file is not actually in the directory represented by the
            # context then we create and bind a reference to it.
            if obj.parent.path != context.path:
                state = Reference(
                    class_name = obj.__class__.__name__,
                    addresses  = [Address(type='file', content=obj.path)]
                )

        return state

### EOF #######################################################################
