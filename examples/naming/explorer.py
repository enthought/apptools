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
""" A naming system explorer. """


# Standard library imports.
import os, sys

# FIXME: The below won't work in an egg-based distribution.  The real question
# is why it was here in the first place.
## Put the Enthought library on the Python path.
#sys.path.append(os.path.abspath(r'..\..\..'))

# Enthought library imports.
from apptools.naming.api import Binding, Context
from apptools.naming.api import PyFSContext
from apptools.naming.adapter import *
from apptools.naming.ui.explorer import Explorer
from pyface.api import GUI
from traits.api import TraitDict, TraitList
from traits.adaptation.api import register_factory
from traits.util.resource import find_resource


# Application entry point.
if __name__ == '__main__':

    # Create the GUI (this does NOT start the GUI event loop).
    gui = GUI()


    # Add some interesting context adapters.
    #
    # Trait dictionaries.
    register_factory(TraitDictContextAdapter, TraitDict, Context)

    # Trait lists.
    register_factory(TraitListContextAdapter, TraitList, Context)

    # Python dictionaries.
    register_factory(DictContextAdapter, dict, Context)

    # Python lists.
    register_factory(ListContextAdapter, list, Context)

    # Python objects.
    register_factory(InstanceContextAdapter, type, Context)

    # Get the path to the data directory
    data_path = os.path.join('examples','naming','data')
    full_path = find_resource('AppTools', data_path, alt_path='data',
        return_path=True)

    # Create the root context.
    root = PyFSContext(path=full_path)

    # Create and open the main window.
    window = Explorer(root=Binding(name='Root', obj=root))
    window.open()

    # Start the GUI event loop.
    gui.start_event_loop()
