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
from apptools.naming.api import Binding, Context, ContextAdapterFactory
from apptools.naming.api import PyFSContext
from apptools.naming.adapter import *
from apptools.naming.ui.explorer import Explorer
from pyface.api import GUI
from traits.api import TraitDict, TraitList
from apptools.type_manager import TypeManager
from traits.util.resource import find_resource


# Application entry point.
if __name__ == '__main__':

    # Create the GUI (this does NOT start the GUI event loop).
    gui = GUI()

    # Create a type manager to manage context adapters.
    type_manager = TypeManager()

    # Add some interesting context adapters.
    #
    # Trait dictionaries.
    type_manager.register_type_adapters(
        ContextAdapterFactory(
            adaptee_class=TraitDict, adapter_class=TraitDictContextAdapter,
        ),

        TraitDict
    )

    # Trait lists.
    type_manager.register_type_adapters(
        ContextAdapterFactory(
            adaptee_class=TraitList, adapter_class=TraitListContextAdapter,
        ),

        TraitList
    )

    # Python dictionaries.
    type_manager.register_type_adapters(
        ContextAdapterFactory(
            adaptee_class=dict, adapter_class=DictContextAdapter,
        ),

        dict
    )

    # Python lists.
    type_manager.register_type_adapters(
        ContextAdapterFactory(
            adaptee_class=list, adapter_class=ListContextAdapter,
        ),

        list
    )

    # Python objects.
    type_manager.register_type_adapters(
        InstanceContextAdapterFactory(), object
    )

    # Get the path to the data directory
    data_path = os.path.join('examples','naming','data')
    full_path = find_resource('AppTools', data_path, alt_path='data',
        return_path=True)

    # Create the root context.
    root = PyFSContext(path=full_path)
    root.environment[Context.TYPE_MANAGER] = type_manager

    # Create and open the main window.
    window = Explorer(root=Binding(name='Root', obj=root))
    window.open()

    # Start the GUI event loop.
    gui.start_event_loop()

##### EOF #####################################################################
