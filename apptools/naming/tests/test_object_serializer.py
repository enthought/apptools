# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
import os
import shutil
import tempfile
import unittest

from traits.api import cached_property, HasTraits, Property, Str, Event

from apptools.naming.api import ObjectSerializer


class FooWithTraits(HasTraits):
    """Dummy HasTraits class for testing ObjectSerizalizer."""

    full_name = Str()

    last_name = Property(observe="full_name")

    event = Event()

    @cached_property
    def _get_last_name(self):
        return self.full_name.split(" ")[-1]


class TestObjectSerializer(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir)
        self.tmp_file = os.path.join(self.tmpdir, "tmp.pickle")

    def test_save_load_roundtrip(self):
        # Test HasTraits objects can be serialized and deserialized as expected
        obj = FooWithTraits(full_name="John Doe")

        serializer = ObjectSerializer()
        serializer.save(self.tmp_file, obj)

        self.assertTrue(serializer.can_load(self.tmp_file))
        deserialized = serializer.load(self.tmp_file)

        self.assertIsInstance(deserialized, FooWithTraits)
        self.assertEqual(deserialized.full_name, "John Doe")
        self.assertEqual(deserialized.last_name, "Doe")
