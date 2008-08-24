"""Test for the spickle module.

"""
# Author: Prabhu Ramachandran <prabhu@aero.iitb.ac.in>
# Copyright (c) 2007, Enthought, Inc.
# License: BSD Style.


import unittest
import numpy
from pickle import dumps

from enthought.persistence import spickle
from enthought.traits.api import HasTraits, Float, Int

class A:
    def __init__(self):
        self.a = 100
        self.array = numpy.linspace(0, 1, 5)

class B(HasTraits):
    i = Int(10)
    f = Float(1.0)

class Foo(object):
    def __init__(self, a=1):
        self.a = A()
        self.a.b = 200
        self.ref = self.a
        self.b = B()
        self.b.set(i=20, f=2.0)

class TestStatePickler(unittest.TestCase):
    def _test_object(self, x):
        assert x.a.a == 100
        assert numpy.all(x.a.array == numpy.linspace(0, 1, 5))
        assert x.a.b == 200
        assert x.a == x.ref
        assert x.b.i == 20
        assert x.b.f == 2.0

    def test_dump_state(self):
        "Test if we are able to dump the state to a string."
        f = Foo()
        str = dumps(f)
        st = spickle.get_state(f)
        str1 = spickle.dumps_state(st)
        self.assertEqual(str, str1)
        st = spickle.loads_state(str)
        self.assertEqual(str, spickle.dumps_state(st))

    def test_state2object(self):
        "Test if we can convert a state to an object."
        f = Foo()
        str = dumps(f)
        st = spickle.get_state(f)
        g = spickle.state2object(st)
        self._test_object(g)
        

def test_suite():
    """Collects all the tests to be run."""
    suites = []
    suites.append(unittest.makeSuite(TestStatePickler, 'test_'))
    total_suite = unittest.TestSuite(suites)
    return total_suite

def test(verbose=2):
    """Useful when you need to run the tests interactively."""
    all_tests = test_suite()
    runner = unittest.TextTestRunner(verbosity=verbose)
    result = runner.run(all_tests)
    return result, runner

if __name__ == "__main__":
    unittest.main()
