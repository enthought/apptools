# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Tests operations that span contexts. """


# Standard library imports.
import unittest

# Enthought library imports.
from apptools.naming.api import (
    Context,
    InvalidNameError,
    NameAlreadyBoundError,
    NameNotFoundError,
    NotContextError,
    ObjectFactory,
    StateFactory,
)


class ContextTestCase(unittest.TestCase):
    """ Tests naming operations that span contexts. """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        self.context = self.create_context()
        self.context.create_subcontext("sub")

    def tearDown(self):
        """ Called immediately after each test method has been called. """

        self.context = None

    ###########################################################################
    # 'ContextTestCase' interface.
    ###########################################################################

    def create_context(self):
        """ Creates the context that we are testing. """

        return Context()

    ###########################################################################
    # Tests.
    ###########################################################################

    def test_bind(self):
        """ bind """

        # Convenience.
        context = self.context
        sub = self.context.lookup("sub")
        self.assertIsInstance(sub, Context)

        # Make sure that the sub-context is empty.
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Empty name.
        self.assertRaises(InvalidNameError, context.bind, "", 1)

        # Attempt to resolve via a non-existent context.
        self.assertRaises(NameNotFoundError, context.bind, "xx/a", 1)
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Bind a name.
        context.bind("sub/a", 1)
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Attempt to resolve via an existing name that is not a context.
        self.assertRaises(NotContextError, context.bind, "sub/a/xx", 1)
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Try to bind it again.
        self.assertRaises(NameAlreadyBoundError, context.bind, "sub/a", 1)

    def test_bind_with_make_contexts(self):
        """ bind with make contexts """

        # Convenience.
        context = self.context
        sub = self.context.lookup("sub")
        self.assertIsInstance(sub, Context)

        # Make sure that the sub-context is empty.
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Empty name.
        self.assertRaises(InvalidNameError, context.bind, "", 1, True)

        # Attempt to resolve via a non-existent context - which should result
        # in the context being created automatically.
        context.bind("xx/a", 1, True)
        self.assertEqual(len(context.list_bindings("xx")), 1)
        self.assertEqual(1, context.lookup("xx/a"))

        # Bind an even more 'nested' name.
        context.bind("xx/foo/bar/baz", 42, True)
        self.assertEqual(len(context.list_bindings("xx/foo/bar")), 1)
        self.assertEqual(42, context.lookup("xx/foo/bar/baz"))

    def test_rebind(self):
        """ context rebind """

        # Convenience.
        context = self.context
        sub = self.context.lookup("sub")

        # Make sure that the sub-context is empty.
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Empty name.
        self.assertRaises(InvalidNameError, context.rebind, "", 1)

        # Attempt to resolve via a non-existent context.
        self.assertRaises(NameNotFoundError, context.rebind, "xx/a", 1)
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Bind a name.
        context.bind("sub/a", 1)
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Rebind it.
        context.rebind("sub/a", 1)
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Attempt to resolve via an existing name that is not a context.
        self.assertRaises(NotContextError, context.rebind, "sub/a/xx", 1)
        self.assertEqual(len(sub.list_bindings("")), 1)

    def test_rebind_with_make_contexts(self):
        """ rebind with make contexts """

        # Convenience.
        context = self.context
        sub = self.context.lookup("sub")
        self.assertIsInstance(sub, Context)

        # Make sure that the sub-context is empty.
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Empty name.
        self.assertRaises(InvalidNameError, context.rebind, "", 1, True)

        # Attempt to resolve via a non-existent context - which should result
        # in the context being created automatically.
        context.rebind("xx/a", 1, True)
        self.assertEqual(len(context.list_bindings("xx")), 1)
        self.assertEqual(1, context.lookup("xx/a"))

        # Rebind an even more 'nested' name.
        context.rebind("xx/foo/bar/baz", 42, True)
        self.assertEqual(len(context.list_bindings("xx/foo/bar")), 1)
        self.assertEqual(42, context.lookup("xx/foo/bar/baz"))

        # And do it again... (this is REbind after all).
        context.rebind("xx/foo/bar/baz", 42, True)
        self.assertEqual(len(context.list_bindings("xx/foo/bar")), 1)
        self.assertEqual(42, context.lookup("xx/foo/bar/baz"))

    def test_unbind(self):
        """ context unbind """

        # Convenience.
        context = self.context
        sub = self.context.lookup("sub")

        # Make sure that the sub-context is empty.
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Empty name.
        self.assertRaises(InvalidNameError, context.unbind, "")

        # Attempt to resolve via a non-existent context.
        self.assertRaises(NameNotFoundError, context.unbind, "xx/a")
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Bind a name.
        context.bind("sub/a", 1)
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Attempt to resolve via an existing name that is not a context.
        self.assertRaises(NotContextError, context.unbind, "sub/a/xx")
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Unbind it.
        context.unbind("sub/a")
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Try to unbind a non-existent name.
        self.assertRaises(NameNotFoundError, context.unbind, "sub/b")

    def test_rename_object(self):
        """ rename an object """

        # Convenience.
        context = self.context
        sub = self.context.lookup("sub")

        # Make sure that the sub-context is empty.
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Empty name.
        self.assertRaises(InvalidNameError, context.rename, "", "x")
        self.assertRaises(InvalidNameError, context.rename, "x", "")

        # Attempt to resolve via a non-existent context.
        self.assertRaises(NameNotFoundError, context.rename, "x/a", "x/b")
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Bind a name.
        context.bind("sub/a", 1)
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Attempt to resolve via an existing name that is not a context.
        self.assertRaises(NotContextError, context.bind, "sub/a/xx", 1)
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Rename it.
        context.rename("sub/a", "sub/b")
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Lookup using the new name.
        self.assertEqual(context.lookup("sub/b"), 1)

        # Lookup using the old name.
        self.assertRaises(NameNotFoundError, context.lookup, "sub/a")

    def test_rename_context(self):
        """ rename a context """

        # Convenience.
        context = self.context
        sub = self.context.lookup("sub")

        # Make sure that the sub-context is empty.
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Empty name.
        self.assertRaises(InvalidNameError, context.rename, "", "x")
        self.assertRaises(InvalidNameError, context.rename, "x", "")

        # Attempt to resolve via a non-existent context.
        self.assertRaises(NameNotFoundError, context.rename, "x/a", "x/b")
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Create a context.
        context.create_subcontext("sub/a")
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Rename it.
        context.rename("sub/a", "sub/b")
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Lookup using the new name.
        context.lookup("sub/b")

        # Lookup using the old name.
        self.assertRaises(NameNotFoundError, context.lookup, "sub/a")

    def test_lookup(self):
        """ lookup """

        # Convenience.
        context = self.context
        sub = self.context.lookup("sub")

        # Make sure that the sub-context is empty.
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Attempt to resolve via a non-existent context.
        self.assertRaises(NameNotFoundError, context.lookup, "xx/a")
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Bind a name.
        context.bind("sub/a", 1)
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Attempt to resolve via an existing name that is not a context.
        self.assertRaises(NotContextError, context.lookup, "sub/a/xx")
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Look it up.
        self.assertEqual(context.lookup("sub/a"), 1)

        # Looking up the Empty name returns the context itself.
        self.assertEqual(context.lookup(""), context)

        # Non-existent name.
        self.assertRaises(NameNotFoundError, context.lookup, "sub/b")

    def test_create_subcontext(self):
        """ create sub-context """

        # Convenience.
        context = self.context
        sub = self.context.lookup("sub")

        # Make sure that the sub-context is empty.
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Empty name.
        self.assertRaises(InvalidNameError, context.create_subcontext, "")

        # Attempt to resolve via a non-existent context.
        self.assertRaises(NameNotFoundError, context.create_subcontext, "xx/a")
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Create a sub-context.
        context.create_subcontext("sub/a")
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Try to bind it again.
        self.assertRaises(
            NameAlreadyBoundError, context.create_subcontext, "sub/a"
        )

        # Bind a name.
        context.bind("sub/b", 1)
        self.assertEqual(len(sub.list_bindings("")), 2)

        # Attempt to resolve via an existing name that is not a context.
        self.assertRaises(
            NotContextError, context.create_subcontext, "sub/b/xx"
        )
        self.assertEqual(len(sub.list_bindings("")), 2)

    def test_destroy_subcontext(self):
        """ single context destroy sub-context """

        # Convenience.
        context = self.context
        sub = self.context.lookup("sub")

        # Make sure that the sub-context is empty.
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Empty name.
        self.assertRaises(InvalidNameError, context.destroy_subcontext, "")

        # Attempt to resolve via a non-existent context.
        self.assertRaises(
            NameNotFoundError, context.destroy_subcontext, "xx/a"
        )
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Create a sub-context.
        context.create_subcontext("sub/a")
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Destroy it.
        context.destroy_subcontext("sub/a")
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Bind a name.
        context.bind("sub/a", 1)
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Try to destroy it.
        self.assertRaises(NotContextError, context.destroy_subcontext, "sub/a")

        # Try to destroy a non-existent name.
        self.assertRaises(
            NameNotFoundError, context.destroy_subcontext, "sub/b"
        )

        # Attempt to resolve via an existing name that is not a context.
        self.assertRaises(
            NotContextError, context.destroy_subcontext, "sub/a/xx"
        )
        self.assertEqual(len(sub.list_bindings("")), 1)

    def test_list_bindings(self):
        """ list bindings """

        # Convenience.
        context = self.context
        sub = self.context.lookup("sub")

        # List the bindings in the root.
        bindings = context.list_bindings("")
        self.assertEqual(len(bindings), 1)

        # List the names in the sub-context.
        bindings = context.list_bindings("sub")
        self.assertEqual(len(bindings), 0)

        # Attempt to resolve via a non-existent context.
        self.assertRaises(NameNotFoundError, context.list_bindings, "xx/a")
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Bind a name.
        context.bind("sub/a", 1)
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Attempt to resolve via an existing name that is not a context.
        self.assertRaises(NotContextError, context.list_bindings, "sub/a/xx")
        self.assertEqual(len(sub.list_bindings("")), 1)

    def test_list_names(self):
        """ list names """

        # Convenience.
        context = self.context
        sub = self.context.lookup("sub")

        # List the names in the root.
        names = context.list_names("")
        self.assertEqual(len(names), 1)

        # List the names in the sub-context.
        names = context.list_names("sub")
        self.assertEqual(len(names), 0)

        # Attempt to resolve via a non-existent context.
        self.assertRaises(NameNotFoundError, context.list_names, "xx/a")
        self.assertEqual(len(sub.list_bindings("")), 0)

        # Bind a name.
        context.bind("sub/a", 1)
        self.assertEqual(len(sub.list_bindings("")), 1)

        # Attempt to resolve via an existing name that is not a context.
        self.assertRaises(NotContextError, context.list_names, "sub/a/xx")
        self.assertEqual(len(sub.list_bindings("")), 1)

    def test_default_factories(self):
        """ default object and state factories. """

        object_factory = ObjectFactory()
        self.assertRaises(
            NotImplementedError, object_factory.get_object_instance, 0, 0, 0
        )

        state_factory = StateFactory()
        self.assertRaises(
            NotImplementedError, state_factory.get_state_to_bind, 0, 0, 0
        )

    def test_search(self):
        """ test retrieving the names of bound objects """

        # Convenience.
        context = self.context
        sub = self.context.lookup("sub")
        context.create_subcontext("sub sibling")
        sub_sub = sub.create_subcontext("sub sub")

        context.bind("one", 1)
        names = context.search(1)
        self.assertEqual(len(names), 1)
        self.assertEqual(names[0], "one")

        names = sub.search(1)
        self.assertEqual(len(names), 0)

        context.bind("sub/two", 2)
        names = context.search(2)
        self.assertEqual(len(names), 1)
        self.assertEqual(names[0], "sub/two")

        names = sub.search(2)
        self.assertEqual(len(names), 1)
        self.assertEqual(names[0], "two")

        context.bind("sub/sub sub/one", 1)
        names = context.search(1)
        self.assertEqual(len(names), 2)
        self.assertEqual(sorted(names), sorted(["one", "sub/sub sub/one"]))

        names = sub.search(None)
        self.assertEqual(len(names), 0)

        names = context.search(sub_sub)
        self.assertEqual(len(names), 1)
        self.assertEqual(names[0], "sub/sub sub")
