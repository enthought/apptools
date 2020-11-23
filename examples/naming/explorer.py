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

# Enthought library imports.
from apptools.naming.api import Binding
from apptools.naming.api import PyContext
from apptools.naming.ui.explorer import Explorer
from pyface.api import GUI
from traits.api import HasTraits, Instance, List, Str


class Foo(HasTraits):
    name = Str()
    names = List(Str())


class Bar(HasTraits):
    foo = Instance(Foo)


# Application entry point.
if __name__ == '__main__':

    # Create the GUI (this does NOT start the GUI event loop).
    gui = GUI()

    # Create the root context.
    root = PyContext(namespace=Bar(foo=Foo(name="Hello", names=["1", "2"])))

    # Create and open the main window.
    window = Explorer(root=Binding(name='Root', obj=root))
    window.open()

    # Start the GUI event loop.
    gui.start_event_loop()
