# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" The initial context factory for Python file system contexts. """


# Local imports.
from .context import Context
from .initial_context_factory import InitialContextFactory
from .object_serializer import ObjectSerializer
from .pyfs_context import PyFSContext
from .pyfs_context_factory import PyFSContextFactory
from .pyfs_object_factory import PyFSObjectFactory
from .pyfs_state_factory import PyFSStateFactory


class PyFSInitialContextFactory(InitialContextFactory):
    """ The initial context factory for Python file system contexts. """

    ###########################################################################
    # 'InitialContextFactory' interface.
    ###########################################################################

    def get_initial_context(self, environment):
        """ Creates an initial context for beginning name resolution. """

        # Object factories.
        object_factories = [PyFSObjectFactory(), PyFSContextFactory()]
        environment[Context.OBJECT_FACTORIES] = object_factories

        # State factories.
        state_factories = [PyFSStateFactory()]
        environment[Context.STATE_FACTORIES] = state_factories

        # Object serializers.
        object_serializers = [ObjectSerializer()]
        environment[PyFSContext.OBJECT_SERIALIZERS] = object_serializers

        return PyFSContext(path=r"", environment=environment)
