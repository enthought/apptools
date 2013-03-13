import unittest

from ..type_registry import LazyRegistry

from .dummies import A, B, C, D, Mixed, Abstract, Concrete, ConcreteSubclass


class TestLazyRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = LazyRegistry()
        # Bodge in a different importer.
        self.registry._import_object = 'Imported {0}'.format

    def test_deferred_push(self):
        self.registry.push('dummies:A', 'foo:A')
        self.registry.push('dummies:C', 'foo:C')
        self.assertEqual(self.registry.lookup_by_type(A), 'Imported foo:A')
        self.assertEqual(self.registry.lookup_by_type(B), 'Imported foo:A')
        self.assertEqual(self.registry.lookup_by_type(C), 'Imported foo:C')
        self.assertRaises(KeyError, self.registry.lookup_by_type, D)

    def test_greedy_push(self):
        self.registry.push(A, 'foo:A')
        self.registry.push(C, 'foo:C')
        self.assertEqual(self.registry.lookup_by_type(A), 'Imported foo:A')
        self.assertEqual(self.registry.lookup_by_type(B), 'Imported foo:A')
        self.assertEqual(self.registry.lookup_by_type(C), 'Imported foo:C')
        self.assertRaises(KeyError, self.registry.lookup_by_type, D)

    def test_mro(self):
        self.registry.push('dummies:A', 'foo:A')
        self.registry.push('dummies:D', 'foo:D')
        self.assertEqual(self.registry.lookup_by_type(Mixed), 'Imported foo:A')

    def test_lookup_instance(self):
        self.registry.push(A, 'foo:A')
        self.registry.push(C, 'foo:C')
        self.assertEqual(self.registry.lookup(A()), 'Imported foo:A')
        self.assertEqual(self.registry.lookup(B()), 'Imported foo:A')
        self.assertEqual(self.registry.lookup(C()), 'Imported foo:C')
        self.assertRaises(KeyError, self.registry.lookup, D())

    def test_abc(self):
        self.registry.push_abc(Abstract, 'foo:Abstract')
        self.assertEqual(self.registry.lookup_by_type(Concrete),
            'Imported foo:Abstract')
        self.assertEqual(self.registry.lookup_by_type(ConcreteSubclass),
            'Imported foo:Abstract')
