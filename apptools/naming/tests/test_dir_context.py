# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Tests the default directory context. """


# Enthought library imports.
from apptools.naming.api import (
    DirContext,
    NameNotFoundError,
    NotContextError,
)

# Local imports.
from .test_context import ContextTestCase


class DirContextTestCase(ContextTestCase):
    """ Tests the default directory context. """

    ###########################################################################
    # 'ContextTestCase' interface.
    ###########################################################################

    def create_context(self):
        """ Creates the context that we are testing. """

        return DirContext()

    ###########################################################################
    # Tests.
    ###########################################################################

    def test_get_attributes(self):
        """ get attributes """

        # Convenience.
        context = self.context
        sub = self.context.lookup("sub")
        self.assertIsInstance(sub, DirContext)

        #### Generic name resolution tests ####

        # Non-existent name.
        self.assertRaises(NameNotFoundError, context.get_attributes, "x")

        # Attempt to resolve via a non-existent context.
        self.assertRaises(NameNotFoundError, context.get_attributes, "x/a")

        # Attempt to resolve via an existing name that is not a context.
        context.bind("sub/a", 1)
        self.assertEqual(len(sub.list_bindings("")), 1)
        self.assertRaises(NotContextError, context.get_attributes, "sub/a/x")

        #### Operation specific tests ####

        # Attributes of the root context.
        attributes = self.context.get_attributes("")
        self.assertEqual(len(attributes), 0)

        # Attributes of a sub-context.
        attributes = context.get_attributes("sub")
        self.assertEqual(len(attributes), 0)

    def test_set_get_attributes(self):
        """ get and set attributes """

        defaults = {"colour": "blue"}

        # Convenience.
        context = self.context
        sub = self.context.lookup("sub")
        self.assertIsInstance(sub, DirContext)

        #### Generic name resolution tests ####

        # Non-existent name.
        self.assertRaises(
            NameNotFoundError, context.set_attributes, "x", defaults
        )

        # Attempt to resolve via a non-existent context.
        self.assertRaises(
            NameNotFoundError, context.set_attributes, "x/a", defaults
        )

        # Attempt to resolve via an existing name that is not a context.
        context.bind("sub/a", 1)
        self.assertEqual(len(sub.list_bindings("")), 1)
        self.assertRaises(
            NotContextError, context.set_attributes, "sub/a/xx", defaults
        )

        #### Operation specific tests ####

        # Attributes of the root context.
        attributes = self.context.get_attributes("")
        self.assertEqual(len(attributes), 0)

        # Set the attributes.
        context.set_attributes("", defaults)
        attributes = context.get_attributes("")
        self.assertEqual(len(attributes), 1)
        self.assertEqual(attributes["colour"], "blue")

        # Attributes of a sub-context.
        attributes = context.get_attributes("sub")
        self.assertEqual(len(attributes), 0)

        # Set the attributes.
        context.set_attributes("sub", defaults)
        attributes = context.get_attributes("sub")
        self.assertEqual(len(attributes), 1)
        self.assertEqual(attributes["colour"], "blue")
