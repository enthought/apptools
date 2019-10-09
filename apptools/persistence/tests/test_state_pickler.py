"""Unit tests for the state pickler and unpickler.

"""
# Author: Prabhu Ramachandran <prabhu_r@users.sf.net>
# Copyright (c) 2005-2015, Enthought, Inc.
# License: BSD Style.

import base64
import pickle
import unittest
import math
import os
import tempfile

import numpy

from traits.api import Bool, Int, Long, Array, Float, Complex, Any, \
    Str, Unicode, Instance, Tuple, List, Dict, HasTraits

try:
    from tvtk.api import tvtk
except ImportError:
    TVTK_AVAILABLE = False
else:
    TVTK_AVAILABLE = True

from apptools.persistence import state_pickler


# A simple class to test instances.
class A(object):

    def __init__(self):
        self.a = 'a'

# NOTE: I think that TVTK specific testing should be moved to the
#       TVTK package.


# A classic class for testing the pickler.
class TestClassic:

    def __init__(self):
        self.b = False
        self.i = 7
        self.l = 1234567890123456789
        self.f = math.pi
        self.c = complex(1.01234, 2.3)
        self.n = None
        self.s = 'String'
        self.u = u'Unicode'
        self.inst = A()
        self.tuple = (1, 2, 'a', A())
        self.list = [1, 1.1, 'a', 1j, self.inst]
        self.pure_list = list(range(5))
        self.dict = {'a': 1, 'b': 2, 'ref': self.inst}
        self.numeric = numpy.ones((2, 2, 2), 'f')
        self.ref = self.numeric
        if TVTK_AVAILABLE:
            self._tvtk = tvtk.Property()


# A class with traits for testing the pickler.
class TestTraits(HasTraits):
    b = Bool(False)
    i = Int(7)
    l = Long(12345678901234567890)
    f = Float(math.pi)
    c = Complex(complex(1.01234, 2.3))
    n = Any
    s = Str('String')
    u = Unicode(u'Unicode')
    inst = Instance(A)
    tuple = Tuple
    list = List
    pure_list = List(list(range(5)))
    dict = Dict
    numeric = Array(value=numpy.ones((2, 2, 2), 'f'))
    ref = Array
    if TVTK_AVAILABLE:
        _tvtk = Instance(tvtk.Property, ())

    def __init__(self):
        self.inst = A()
        self.tuple = (1, 2, 'a', A())
        self.list = [1, 1.1, 'a', 1j, self.inst]
        self.dict = {'a': 1, 'b': 2, 'ref': self.inst}
        self.ref = self.numeric


class TestDictPickler(unittest.TestCase):

    def set_object(self, obj):
        """Changes the objects properties to test things."""
        obj.b = True
        obj.i = 8
        obj.s = 'string'
        obj.u = u'unicode'
        obj.inst.a = 'b'
        obj.list[0] = 2
        obj.tuple[-1].a = 't'
        obj.dict['a'] = 10
        if TVTK_AVAILABLE:
            obj._tvtk.trait_set(
                point_size=3, specular_color=(1, 0, 0),
                representation='w'
            )

    def _check_instance_and_references(self, obj, data):
        """Asserts that there is one instance and two references in the state.
        We need this as there isn't a guarantee as to which will be the
        reference and which will be the instance.
        """
        inst = data['inst']
        list_end = data['list']['data'][-1]
        dict_ref = data['dict']['data']['ref']
        all_inst = [inst, list_end, dict_ref]
        types = [x['type'] for x in all_inst]
        self.assertEqual(types.count('instance'), 1)
        self.assertEqual(types.count('reference'), 2)
        inst_state = all_inst[types.index('instance')]
        self.assertEqual(inst_state['data']['data']['a'], 'b')

    def verify(self, obj, state):
        data = state['data']
        self.assertEqual(state['class_name'], obj.__class__.__name__)
        data = data['data']
        self.assertEqual(data['b'], obj.b)
        self.assertEqual(data['i'], obj.i)
        self.assertEqual(data['l'], obj.l)
        self.assertEqual(data['f'], obj.f)
        self.assertEqual(data['c'], obj.c)
        self.assertEqual(data['n'], obj.n)
        self.assertEqual(data['s'], obj.s)
        self.assertEqual(data['u'], obj.u)
        tup = data['tuple']['data']
        self.assertEqual(tup[:-1], obj.tuple[:-1])
        self.assertEqual(tup[-1]['data']['data']['a'], 't')
        lst = data['list']['data']
        self.assertEqual(lst[:-1], obj.list[:-1])

        pure_lst = data['pure_list']['data']
        self.assertEqual(pure_lst, obj.pure_list)
        dct = data['dict']['data']
        self.assertEqual(dct['a'], obj.dict['a'])
        self.assertEqual(dct['b'], obj.dict['b'])

        self._check_instance_and_references(obj, data)

        num_attr = 'numeric' if data['numeric']['type'] == 'numeric' else 'ref'
        decodestring = getattr(base64, 'decodebytes', base64.decodestring)
        junk = state_pickler.gunzip_string(
            decodestring(data[num_attr]['data'])
        )
        num = pickle.loads(junk)
        self.assertEqual(numpy.alltrue(numpy.ravel(num == obj.numeric)), 1)

        self.assertTrue(data['ref']['type'] in ['reference', 'numeric'])
        if data['ref']['type'] == 'numeric':
            self.assertEqual(data['numeric']['type'], 'reference')
        else:
            self.assertEqual(data['numeric']['type'], 'numeric')
        self.assertEqual(data['ref']['id'], data['numeric']['id'])

    def verify_unpickled(self, obj, state):
        self.assertEqual(state.__metadata__['class_name'],
                         obj.__class__.__name__)
        self.assertEqual(state.b, obj.b)
        self.assertEqual(state.i, obj.i)
        self.assertEqual(state.l, obj.l)
        self.assertEqual(state.f, obj.f)
        self.assertEqual(state.c, obj.c)
        self.assertEqual(state.n, obj.n)
        self.assertEqual(state.s, obj.s)
        self.assertEqual(state.u, obj.u)
        self.assertEqual(state.inst.__metadata__['type'], 'instance')

        tup = state.tuple
        self.assertEqual(state.tuple.has_instance, True)
        self.assertEqual(tup[:-1], obj.tuple[:-1])
        self.assertEqual(tup[-1].a, 't')
        lst = state.list
        self.assertEqual(state.list.has_instance, True)
        self.assertEqual(lst[:-1], obj.list[:-1])
        # Make sure the reference is the same
        self.assertEqual(id(state.inst), id(lst[-1]))

        self.assertEqual(lst[-1].a, 'b')

        pure_lst = state.pure_list
        self.assertEqual(pure_lst, obj.pure_list)
        self.assertEqual(state.pure_list.has_instance, False)

        dct = state.dict
        self.assertEqual(dct.has_instance, True)
        self.assertEqual(dct['a'], obj.dict['a'])
        self.assertEqual(dct['b'], obj.dict['b'])
        self.assertEqual(dct['ref'].__metadata__['type'], 'instance')

        num = state.numeric
        self.assertEqual(numpy.alltrue(numpy.ravel(num == obj.numeric)), 1)
        self.assertEqual(id(state.ref), id(num))

        if TVTK_AVAILABLE:
            _tvtk = state._tvtk
            self.assertEqual(_tvtk.representation, obj._tvtk.representation)
            self.assertEqual(_tvtk.specular_color, obj._tvtk.specular_color)
            self.assertEqual(_tvtk.point_size, obj._tvtk.point_size)

    def verify_state(self, state1, state):
        self.assertEqual(state.__metadata__,
                         state1.__metadata__)
        self.assertEqual(state.b, state1.b)
        self.assertEqual(state.i, state1.i)
        self.assertEqual(state.l, state1.l)
        self.assertEqual(state.f, state1.f)
        self.assertEqual(state.c, state1.c)
        self.assertEqual(state.n, state1.n)
        self.assertEqual(state.s, state1.s)
        self.assertEqual(state.u, state1.u)
        # The ID's need not be identical so we equate them here so the
        # tests pass.  Note that the ID's only need be consistent not
        # identical!
        if TVTK_AVAILABLE:
            instances = ('inst', '_tvtk')
        else:
            instances = ('inst',)

        for attr in instances:
            getattr(state1, attr).__metadata__['id'] = \
                getattr(state, attr).__metadata__['id']

        if TVTK_AVAILABLE:
            self.assertEqual(state1._tvtk, state._tvtk)

        state1.tuple[-1].__metadata__['id'] = \
            state.tuple[-1].__metadata__['id']
        self.assertEqual(state.inst.__metadata__, state1.inst.__metadata__)

        self.assertEqual(state.tuple, state1.tuple)
        self.assertEqual(state.list, state1.list)

        self.assertEqual(state.pure_list, state1.pure_list)

        self.assertEqual(state.dict, state1.dict)

        self.assertEqual((state1.numeric == state.numeric).all(), True)
        self.assertEqual(id(state.ref), id(state.numeric))
        self.assertEqual(id(state1.ref), id(state1.numeric))


    def test_has_instance(self):
        """Test to check has_instance correctness."""
        a = A()
        r = state_pickler.get_state(a)
        self.assertEqual(r.__metadata__['has_instance'], True)
        l = [1, a]
        r = state_pickler.get_state(l)
        self.assertEqual(r.has_instance, True)
        self.assertEqual(r[1].__metadata__['has_instance'], True)
        d = {'a': l, 'b': 1}
        r = state_pickler.get_state(d)
        self.assertEqual(r.has_instance, True)
        self.assertEqual(r['a'].has_instance, True)
        self.assertEqual(r['a'][1].__metadata__['has_instance'], True)

        class B:

            def __init__(self):
                self.a = [1, A()]

        b = B()
        r = state_pickler.get_state(b)
        self.assertEqual(r.__metadata__['has_instance'], True)
        self.assertEqual(r.a.has_instance, True)
        self.assertEqual(r.a[1].__metadata__['has_instance'], True)

    def test_pickle_classic(self):
        """Test if classic classes can be pickled."""
        t = TestClassic()
        self.set_object(t)
        # Generate the dict that is actually pickled.
        state = state_pickler.StatePickler().dump_state(t)

        # First check if all the attributes are handled.
        keys = sorted(state['data']['data'].keys())
        expect = [x for x in t.__dict__.keys() if '__' not in x]
        expect.sort()
        self.assertEqual(keys, expect)
        # Check each attribute.
        self.verify(t, state)

    def test_unpickle_classic(self):
        """Test if classic classes can be unpickled."""
        t = TestClassic()
        self.set_object(t)
        # Get the pickled state.
        res = state_pickler.get_state(t)
        # Check each attribute.
        self.verify_unpickled(t, res)

    def test_state_setter_classic(self):
        """Test if classic classes' state can be set."""
        t = TestClassic()
        self.set_object(t)
        # Get the pickled state.
        res = state_pickler.get_state(t)

        # Now create a new instance and set its state.
        t1 = state_pickler.create_instance(res)
        state_pickler.set_state(t1, res)
        # Check each attribute.
        self.verify_unpickled(t1, res)

    def test_state_setter(self):
        """Test some of the features of the set_state method."""
        t = TestClassic()
        self.set_object(t)
        # Get the saved state.
        res = state_pickler.get_state(t)

        # Now create a new instance and test the setter.
        t1 = state_pickler.create_instance(res)

        keys = ['c', 'b', 'f', 'i', 'tuple', 'list', 'l', 'numeric',
                'n', 's', 'u', 'pure_list', 'inst', 'ref', 'dict']
        ignore = list(keys)
        ignore.remove('b')
        first = ['b']
        last = []
        state_pickler.set_state(t1, res, ignore=ignore, first=first, last=last)
        # Only 'b' should have been set.
        self.assertEqual(t1.b, True)
        # Rest are unchanged.
        self.assertEqual(t1.i, 7)
        self.assertEqual(t1.s, 'String')
        self.assertEqual(t1.u, u'Unicode')
        self.assertEqual(t1.inst.a, 'a')
        self.assertEqual(t1.list[0], 1)
        self.assertEqual(t1.tuple[-1].a, 'a')
        self.assertEqual(t1.dict['a'], 1)

        # Check if last works.
        last = ignore
        ignore = []
        first = []
        state_pickler.set_state(t1, res, ignore=ignore, first=first, last=last)
        # Check everything.
        self.verify_unpickled(t1, res)

    def test_pickle_traits(self):
        """Test if traited classes can be pickled."""
        t = TestTraits()
        self.set_object(t)

        # Generate the dict that is actually pickled.
        state = state_pickler.StatePickler().dump_state(t)

        # First check if all the attributes are handled.
        keys = sorted(state['data']['data'].keys())
        expect = [x for x in t.__dict__.keys() if '__' not in x]
        expect.sort()
        self.assertEqual(keys, expect)
        # Check each attribute.
        self.verify(t, state)

    def test_unpickle_traits(self):
        """Test if traited classes can be unpickled."""
        t = TestTraits()
        self.set_object(t)

        # Get the pickled state.
        res = state_pickler.get_state(t)
        # Check each attribute.
        self.verify_unpickled(t, res)

    def test_state_setter_traits(self):
        """Test if traited classes' state can be set."""
        t = TestTraits()
        self.set_object(t)

        # Get the saved state.
        res = state_pickler.get_state(t)

        # Now create a new instance and set its state.
        t1 = state_pickler.create_instance(res)
        state_pickler.set_state(t1, res)
        # Check each attribute.
        self.verify_unpickled(t1, res)

    def test_reference_cycle(self):
        """Test if reference cycles are handled when setting the state."""
        class A:
            pass

        class B:
            pass
        a = A()
        b = B()
        a.a = b
        b.b = a
        state = state_pickler.get_state(a)
        z = A()
        z.a = B()
        z.a.b = z
        state_pickler.set_state(z, state)

    def test_get_state_on_tuple_with_numeric_references(self):
        num = numpy.zeros(10, float)
        data = (num, num)
        # If this just completes without error, we are good.
        state = state_pickler.get_state(data)
        # The two should be the same object.
        self.assertTrue(state[0] is state[1])
        numpy.testing.assert_allclose(state[0], num)

    def test_state_is_saveable(self):
        """Test if the state can be saved like the object itself."""
        t = TestClassic()
        self.set_object(t)
        state = state_pickler.get_state(t)
        # Now get the state of the state itself.
        state1 = state_pickler.get_state(state)
        self.verify_state(state1, state)

        # Same thing for the traited class.
        t = TestTraits()
        self.set_object(t)
        state = state_pickler.get_state(t)
        # Now get the state of the state itself.
        state1 = state_pickler.get_state(state)
        self.verify_state(state1, state)

    def test_get_pure_state(self):
        """Test if get_pure_state is called first."""
        class B:

            def __init__(self):
                self.a = 'dict'

            def __get_pure_state__(self):
                return {'a': 'get_pure_state'}

            def __getstate__(self):
                return {'a': 'getstate'}
        b = B()
        s = state_pickler.get_state(b)
        self.assertEqual(s.a, 'get_pure_state')
        del B.__get_pure_state__
        s = state_pickler.get_state(b)
        self.assertEqual(s.a, 'getstate')
        del B.__getstate__
        s = state_pickler.get_state(b)
        self.assertEqual(s.a, 'dict')

    def test_dump_to_file_str(self):
        """Test if dump can take a str as file"""
        obj = A()

        filepath = os.path.join(tempfile.gettempdir(), "tmp.file")

        try:
            state_pickler.dump(obj, filepath)
        finally:
            os.remove(filepath)


if __name__ == "__main__":
    unittest.main()
