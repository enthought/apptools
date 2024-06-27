# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Object factory for Python namespace contexts. """


# Local imports.
from .object_factory import ObjectFactory
from .reference import Reference


class PyObjectFactory(ObjectFactory):
    """ Object factory for Python namespace contexts. """

    ###########################################################################
    # 'ObjectFactory' interface.
    ###########################################################################

    def get_object_instance(self, state, name, context):
        """ Creates an object using the specified state information. """

        obj = None

        if isinstance(state, Reference):
            if len(state.addresses) > 0:
                if state.addresses[0].type == "py_context":
                    namespace = state.addresses[0].content
                    obj = context._context_factory(name, namespace)

        elif hasattr(state, "__dict__"):
            from apptools.naming.py_context import PyContext

            if not isinstance(state, PyContext):
                obj = context._context_factory(name, state)

        return obj
