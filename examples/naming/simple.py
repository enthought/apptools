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
""" A simple naming example. """


# Standard library imports.
import os, sys

# Enthought library imports.
from enthought.naming.api import Context, InitialContext


# Application entry point.
if __name__ == '__main__':

    # Set up the naming environment.
    klass_name = "enthought.naming.InitialContextFactory"
    klass_name = "enthought.naming.PyFSInitialContextFactory"
    environment = {Context.INITIAL_CONTEXT_FACTORY : klass_name}

    # Create an initial context.
    context = InitialContext(environment)
    context.path = os.getcwd()
    print 'Context', context, context.path
    print 'Names', context.list_names('')

##### EOF #####################################################################
