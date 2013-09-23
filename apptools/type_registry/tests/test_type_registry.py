import unittest

from ..type_registry import TypeRegistry

from .dummies import A, B, C, D, Mixed, Abstract, Concrete, ConcreteSubclass


class TestTypeRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = TypeRegistry()

    def test_deferred_push(self):
        self.registry.push('dummies:A', 'A')
        self.registry.push('dummies:C', 'C')
        self.assertEqual(self.registry.lookup_by_type(A), 'A')
        self.assertEqual(self.registry.lookup_by_type(B), 'A')
        self.assertEqual(self.registry.lookup_by_type(C), 'C')
        self.assertRaises(KeyError, self.registry.lookup_by_type, D)

    def test_greedy_push(self):
        self.registry.push(A, 'A')
        self.registry.push(C, 'C')
        self.assertEqual(self.registry.lookup_by_type(A), 'A')
        self.assertEqual(self.registry.lookup_by_type(B), 'A')
        self.assertEqual(self.registry.lookup_by_type(C), 'C')
        self.assertRaises(KeyError, self.registry.lookup_by_type, D)

    def test_pop_by_name_from_name(self):
        self.registry.push('dummies:A', 'A')
        self.registry.pop('dummies:A')
        self.assertRaises(KeyError, self.registry.lookup_by_type, A)

    def test_pop_by_name_from_type(self):
        self.registry.push(A, 'A')
        self.registry.pop('dummies:A')
        self.assertRaises(KeyError, self.registry.lookup_by_type, A)

    def test_pop_by_type_from_name(self):
        self.registry.push('dummies:A', 'A')
        self.registry.pop(A)
        self.assertRaises(KeyError, self.registry.lookup_by_type, A)

    def test_pop_by_type_from_type(self):
        self.registry.push(A, 'A')
        self.registry.pop(A)
        self.assertRaises(KeyError, self.registry.lookup_by_type, A)

    def test_mro(self):
        self.registry.push('dummies:A', 'A')
        self.registry.push('dummies:D', 'D')
        self.assertEqual(self.registry.lookup_by_type(Mixed), 'A')

    def test_lookup_instance(self):
        self.registry.push(A, 'A')
        self.registry.push(C, 'C')
        self.assertEqual(self.registry.lookup(A()), 'A')
        self.assertEqual(self.registry.lookup(B()), 'A')
        self.assertEqual(self.registry.lookup(C()), 'C')
        self.assertRaises(KeyError, self.registry.lookup, D())

    def test_lookup_all(self):
        self.registry.push(A, 'A')
        self.registry.push(C, 'C')
        self.assertEqual(self.registry.lookup_all(A()), ['A'])
        self.assertEqual(self.registry.lookup_all(B()), ['A'])
        self.registry.push(A, 'A2')
        self.assertEqual(self.registry.lookup_all(A()), ['A', 'A2'])
        self.assertEqual(self.registry.lookup_all(B()), ['A', 'A2'])

    def test_abc(self):
        self.registry.push_abc(Abstract, 'Abstract')
        self.assertEqual(self.registry.lookup_by_type(Concrete), 'Abstract')
        self.assertEqual(self.registry.lookup_by_type(ConcreteSubclass),
            'Abstract')

    def test_stack_type(self):
        self.registry.push(A, 'A1')
        self.registry.push(A, 'A2')
        self.assertEqual(self.registry.lookup_by_type(A), 'A2')
        self.registry.pop(A)
        self.assertEqual(self.registry.lookup_by_type(A), 'A1')
        self.registry.pop(A)
        self.assertRaises(KeyError, self.registry.lookup_by_type, A)
        self.assertRaises(KeyError, self.registry.pop, A)
        self.assertRaises(KeyError, self.registry.pop, 'dummies:A')
        self.assertEqual(self.registry.type_map, {})
        self.assertEqual(self.registry.name_map, {})
        self.assertEqual(self.registry.abc_map, {})

    def test_stack_mixed_type_and_name(self):
        self.registry.push(A, 'A1')
        self.registry.push('dummies:A', 'A2')
        self.assertEqual(self.registry.lookup_by_type(A), 'A2')
        self.registry.pop(A)
        self.assertEqual(self.registry.lookup_by_type(A), 'A1')
        self.registry.pop('dummies:A')
        self.assertRaises(KeyError, self.registry.lookup_by_type, A)
        self.assertRaises(KeyError, self.registry.pop, A)
        self.assertRaises(KeyError, self.registry.pop, 'dummies:A')
        self.assertEqual(self.registry.type_map, {})
        self.assertEqual(self.registry.name_map, {})
        self.assertEqual(self.registry.abc_map, {})

    def test_stack_abc(self):
        self.registry.push_abc(Abstract, 'Abstract1')
        self.registry.push_abc(Abstract, 'Abstract2')
        self.assertEqual(self.registry.lookup_by_type(Concrete), 'Abstract2')
        self.registry.pop(Abstract)
        self.assertEqual(self.registry.lookup_by_type(Concrete), 'Abstract1')
        self.registry.pop(Abstract)
        self.assertRaises(KeyError, self.registry.lookup_by_type, Concrete)
        self.assertRaises(KeyError, self.registry.pop, Abstract)
        self.assertEqual(self.registry.type_map, {})
        self.assertEqual(self.registry.name_map, {})
        self.assertEqual(self.registry.abc_map, {})
