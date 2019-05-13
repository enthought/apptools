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
""" The naming manager. """


# Enthought library imports.
from traits.api import HasTraits


class NamingManager(HasTraits):
    """ The naming manager. """

    ###########################################################################
    # 'NamingManager' interface.
    ###########################################################################

    def get_state_to_bind(self, obj, name, context):
        """ Returns the state of an object for binding.

        The naming manager asks the context for its list of STATE factories
        and then calls them one by one until it gets a non-None result
        indicating that the factory recognised the object and created state
        information for it.

        If none of the factories recognize the object (or if the context
        has no factories) then the object itself is returned.

        """

        # Local imports.
        from .context import Context

        # We get the state factories from the context's environment.
        state_factories = context.environment[Context.STATE_FACTORIES]

        for state_factory in state_factories:
            state = state_factory.get_state_to_bind(obj, name, context)
            if state is not None:
                break

        else:
            state = obj

        return state

    def get_object_instance(self, info, name, context):
        """ Creates an object using the specified state information.

        The naming manager asks the context for its list of OBJECT factories
        and calls them one by one until it gets a non-None result, indicating
        that the factory recognised the information and created an object.

        If none of the factories recognize the state information (or if the
        context has no factories) then the state information itself is
        returned.

        """

        # Local imports.
        from .context import Context

        # We get the object factories from the context's environment.
        object_factories = context.environment[Context.OBJECT_FACTORIES]

        for object_factory in object_factories:
            obj = object_factory.get_object_instance(info, name, context)
            if obj is not None:
                break

        else:
            obj = info

        return obj


# Singleton instance.
naming_manager = NamingManager()

### EOF #######################################################################
