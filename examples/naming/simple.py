# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" A simple naming example. """


# Standard library imports.
import os

# Enthought library imports.
from apptools.naming.api import Context, InitialContext


# Application entry point.
if __name__ == '__main__':

    # Set up the naming environment.
    klass_name = "apptools.naming.InitialContextFactory"
    klass_name = "apptools.naming.PyFSInitialContextFactory"
    environment = {Context.INITIAL_CONTEXT_FACTORY: klass_name}

    # Create an initial context.
    context = InitialContext(environment)
    context.path = os.getcwd()
    print('Context', context, context.path)
    print('Names', context.list_names(''))
