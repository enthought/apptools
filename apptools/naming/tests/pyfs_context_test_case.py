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
""" Tests naming operations on PyFS contexts. """


# Standard library imports.
import os, shutil, unittest

# Enthought library imports.
from apptools.io import File
from apptools.naming.api import *


class PyFSContextTestCase(unittest.TestCase):
    """ Tests naming operations on PyFS contexts. """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        try:
            if os.path.exists('data'): shutil.rmtree('data')
            if os.path.exists('other'): shutil.rmtree('other')

        except:
            pass

        os.mkdir('data')
        os.mkdir('other')

        self.context = PyFSContext(path='data')
        self.context.create_subcontext('sub')
        self.context.bind('x', 123)
        self.context.bind('y', 321)

        return

    def tearDown(self):
        """ Called immediately after each test method has been called. """

        self.context = None

        shutil.rmtree('data')
        shutil.rmtree('other')

        return

    ###########################################################################
    # Tests.
    ###########################################################################

    def test_initialization(self):
        """ initialization of an existing context """

        context = PyFSContext(path='data')
        self.assertEqual(len(context.list_bindings('')), 3)

        return

    def test_initialization_with_empty_environment(self):
        """ initialization with empty environmentt """

        context = PyFSContext(path='other', environment={})
        self.assertEqual(len(context.list_names('')), 0)

        return

    def test_bind(self):
        """ pyfs context bind """

        # Convenience.
        context = self.context
        sub = self.context.lookup('sub')

        # Make sure that the sub-context is empty.
        self.assertEqual(len(sub.list_bindings('')), 0)

        # Empty name.
        self.assertRaises(InvalidNameError, context.bind, '', 1)

        # Bind a local file object.
        f = File(os.path.join(sub.path, 'foo.py'))
        #f.create_file('print "foo!"\n')

        context.bind('sub/foo.py', f)
        self.assertEqual(len(sub.list_bindings('')), 1)

        # Bind a reference to a non-local file.
        f = File('/tmp')
        context.bind('sub/tmp', f)
        self.assertEqual(len(sub.list_bindings('')), 2)
        self.assertEqual(context.lookup('sub/tmp').path, f.path)

        # Bind a reference to a non-local context.
        f = PyFSContext(path='other')
        context.bind('sub/other', f)
        self.assertEqual(len(sub.list_bindings('')), 3)
        self.assert_(f.path in context.lookup('sub/other').path)

        # Bind a Python object.
        context.bind('sub/a', 1)
        self.assertEqual(len(sub.list_bindings('')), 4)

        # Try to bind it again.
        self.assertRaises(NameAlreadyBoundError, context.bind, 'sub/a', 1)

        return

    def test_rebind(self):
        """ pyfs context rebind """

        # Convenience.
        context = self.context
        sub = self.context.lookup('sub')

        # Make sure that the sub-context is empty.
        self.assertEqual(len(sub.list_bindings('')), 0)

        # Empty name.
        self.assertRaises(InvalidNameError, context.rebind, '', 1)

        # Bind a name.
        context.bind('sub/a', 1)
        self.assertEqual(len(sub.list_bindings('')), 1)

        # Rebind it.
        context.rebind('sub/a', 1)
        self.assertEqual(len(sub.list_bindings('')), 1)

        return

    def test_unbind(self):
        """ pyfs context unbind """

        # Convenience.
        context = self.context
        sub = self.context.lookup('sub')

        # Make sure that the sub-context is empty.
        self.assertEqual(len(sub.list_bindings('')), 0)

        # Empty name.
        self.assertRaises(InvalidNameError, context.unbind, '')

        # Bind a name.
        context.bind('sub/a', 1)
        self.assertEqual(len(sub.list_bindings('')), 1)

        # Unbind it.
        context.unbind('sub/a')
        self.assertEqual(len(sub.list_bindings('')), 0)

        # Try to unbind a non-existent name.
        self.assertRaises(NameNotFoundError, context.unbind, 'sub/b')

        return

    def test_rename(self):
        """ multi-context rename """

        # Convenience.
        context = self.context
        sub = self.context.lookup('sub')

        # Make sure that the sub-context is empty.
        self.assertEqual(len(sub.list_bindings('')), 0)

        # Empty name.
        self.assertRaises(InvalidNameError, context.rename, '', 'x')
        self.assertRaises(InvalidNameError, context.rename, 'x', '')

        # Bind a name.
        context.bind('sub/a', 1)
        self.assertEqual(len(sub.list_bindings('')), 1)

        # Rename it.
        context.rename('sub/a', 'sub/b')
        self.assertEqual(len(sub.list_bindings('')), 1)

        # Lookup using the new name.
        self.assertEqual(context.lookup('sub/b'), 1)

        # Lookup using the old name.
        self.assertRaises(NameNotFoundError, context.lookup, 'sub/a')

    def test_lookup(self):
        """ pyfs context lookup """

        # Convenience.
        context = self.context
        sub = self.context.lookup('sub')

        # Make sure that the sub-context is empty.
        self.assertEqual(len(sub.list_bindings('')), 0)

        # Bind a file object.
        f = File(os.path.join(sub.path, 'foo.py'))
        #f.create_file('print "foo!"\n')

        context.bind('sub/foo.py', f)
        self.assertEqual(len(sub.list_bindings('')), 1)

        # Look it up.
        self.assertEqual(context.lookup('sub/foo.py').path, f.path)

        # Bind a Python object.
        context.bind('sub/a', 1)
        self.assertEqual(len(sub.list_bindings('')), 2)

        # Look it up.
        self.assertEqual(context.lookup('sub/a'), 1)

        # Looking up the Empty name returns the context itself.
        self.assertEqual(context.lookup(''), context)

        # Non-existent name.
        self.assertRaises(NameNotFoundError, context.lookup, 'sub/b')

        return

    def test_create_subcontext(self):
        """ pyfs context create sub-context """

        # Convenience.
        context = self.context
        sub = self.context.lookup('sub')

        # Make sure that the sub-context is empty.
        self.assertEqual(len(sub.list_bindings('')), 0)

        # Empty name.
        self.assertRaises(InvalidNameError, context.create_subcontext, '')

        # Create a sub-context.
        a = context.create_subcontext('sub/a')
        self.assertEqual(len(sub.list_bindings('')), 1)
        self.assert_(os.path.isdir(os.path.join(sub.path, 'a')))

        # Try to bind it again.
        self.assertRaises(
            NameAlreadyBoundError, context.create_subcontext, 'sub/a'
        )

        return

    def test_destroy_subcontext(self):
        """ single context destroy sub-context """

        # Convenience.
        context = self.context
        sub = self.context.lookup('sub')

        # Make sure that the sub-context is empty.
        self.assertEqual(len(sub.list_bindings('')), 0)

        # Empty name.
        self.assertRaises(InvalidNameError, context.destroy_subcontext, '')

        # Create a sub-context.
        a = context.create_subcontext('sub/a')
        self.assertEqual(len(sub.list_bindings('')), 1)

        # Destroy it.
        context.destroy_subcontext('sub/a')
        self.assertEqual(len(sub.list_bindings('')), 0)
        self.assert_(not os.path.isdir(os.path.join(sub.path, 'a')))

        # Bind a name.
        context.bind('sub/a', 1)
        self.assertEqual(len(sub.list_bindings('')), 1)

        # Try to destroy it.
        self.assertRaises(
            NotContextError, context.destroy_subcontext, 'sub/a'
        )

        return

        # Try to destroy a non-existent name.
        self.assertRaises(
            NameNotFoundError, context.destroy_subcontext, 'sub/b'
        )

        return

    def test_get_attributes(self):
        """ get attributes """

        # Convenience.
        context = self.context
        sub = self.context.lookup('sub')
        self.assert_(isinstance(sub, DirContext))

        #### Generic name resolution tests ####

        # Non-existent name.
        self.assertRaises(NameNotFoundError, context.get_attributes, 'xx')

        # Attempt to resolve via a non-existent context.
        self.assertRaises(NameNotFoundError, context.get_attributes,'xx/a')

        # Attempt to resolve via an existing name that is not a context.
        context.bind('sub/a', 1)
        self.assertEqual(len(sub.list_bindings('')), 1)
        self.assertRaises(NotContextError,context.get_attributes,'sub/a/x')

        #### Operation specific tests ####

        # Attributes of the root context.
        attributes = context.get_attributes('')
        self.assertEqual(len(attributes), 0)

        # Attributes of a sub-context.
        attributes = context.get_attributes('sub')
        self.assertEqual(len(attributes), 0)

        return

    def test_set_get_attributes(self):
        """ get and set attributes """

        defaults = {'colour' : 'blue'}

        # Convenience.
        context = self.context
        sub = self.context.lookup('sub')
        self.assert_(isinstance(sub, DirContext))

        #### Generic name resolution tests ####

        # Non-existent name.
        self.assertRaises(
            NameNotFoundError, context.set_attributes, 'xx', defaults
        )

        # Attempt to resolve via a non-existent context.
        self.assertRaises(
            NameNotFoundError, context.set_attributes, 'xx/a', defaults
        )

        # Attempt to resolve via an existing name that is not a context.
        context.bind('sub/a', 1)
        self.assertEqual(len(sub.list_bindings('')), 1)
        self.assertRaises(
            NotContextError, context.set_attributes, 'sub/a/xx', defaults
        )

        #### Operation specific tests ####

        # Attributes of the root context.
        attributes = self.context.get_attributes('')
        self.assertEqual(len(attributes), 0)

        # Set the attributes.
        context.set_attributes('', defaults)
        attributes = context.get_attributes('')
        self.assertEqual(len(attributes), 1)
        self.assertEqual(attributes['colour'], 'blue')

        # Attributes of a sub-context.
        attributes = context.get_attributes('sub')
        self.assertEqual(len(attributes), 0)

        # Set the attributes.
        context.set_attributes('sub', defaults)
        attributes = context.get_attributes('sub')
        self.assertEqual(len(attributes), 1)
        self.assertEqual(attributes['colour'], 'blue')

        return

    def test_namespace_name(self):
        """ get the name of a context within its namespace. """

        # Convenience.
        context = self.context
        sub = self.context.lookup('sub')
        self.assert_(isinstance(sub, DirContext))

        self.assertEqual(context.namespace_name, 'data')
        self.assertEqual(sub.namespace_name, 'data/sub')

        return

#### EOF ######################################################################
