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
from apptools.naming.api import Binding, PyContext
from pyface.api import PythonShell, SplitApplicationWindow
from traits.api import Float, Instance, Str

# Local imports.
from .naming_tree import NamingTree


# Factory function for exploring a Python namespace.
def explore(obj):
    """ View a Python object as a naming context. """

    root = Binding(name='root', obj=PyContext(namespace=obj))

    explorer = Explorer(root=root, size=(1200, 400))
    explorer.open()

    return


class Explorer(SplitApplicationWindow):
    """ The main application window. """

    #### 'Window' interface ###################################################

    title = Str('Naming System Explorer')

    #### 'SplitApplicationWindow' interface ###################################

    # The direction in which the panel is split.
    direction = Str('vertical')

    # The ratio of the size of the left/top pane to the right/bottom pane.
    ratio = Float(0.3)

    # The root binding (usually a binding to a context!).
    root = Instance(Binding)

    ###########################################################################
    # Protected 'SplitApplicationWindow' interface.
    ###########################################################################

    def _create_lhs(self, parent):
        """ Creates the left hand side or top depending on the style. """

        return self._create_tree(parent, self.root)

    def _create_rhs(self, parent):
        """ Creates the panel containing the selected preference page. """

        return self._create_python_shell(parent)

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _create_tree(self, parent, root):
        """ Creates the tree. """

        self._tree = tree = NamingTree(parent, root=root)

        return tree.control

    def _create_python_shell(self, parent):
        """ Creates the Python shell. """

        self._python_shell = python_shell = PythonShell(parent)

        # Bind useful names.
        python_shell.bind('widget', self._tree)
        python_shell.bind('w', self._tree)
        python_shell.bind('window', self)
        python_shell.bind('explore', explore)

        # Execute useful commands to bind useful names ;^)
        python_shell.execute_command('from apptools.naming.api import *')

        return python_shell.control

##### EOF #####################################################################
