"""Tests for the version registry.

"""
# Author: Prabhu Ramachandran <prabhu_r@users.sf.net>
# Copyright (c) 2005, Enthought, Inc.
# License: BSD Style.

# Standard library imports.
import sys
from imp import reload
import unittest

# Enthought library imports.
from traits.api import HasTraits

from apptools.persistence import version_registry, state_pickler


class Classic:
    __version__ = 0

class New(object):
    __version__ = 0

class TraitClass(HasTraits):
    __version__ = 0


class Test(New):
    __version__ = 1
    def __init__(self):
        self.a = Classic()

class Handler:
    def __init__(self):
        self.calls = []
    def upgrade(self, state, version):
        self.calls.append(('upgrade', state, version))
    def upgrade1(self, state, version):
        self.calls.append(('upgrade1', state, version))


class TestVersionRegistry(unittest.TestCase):
    def test_get_version(self):
        """Test the get_version function."""
        if sys.version_info[0] > 2:
            extra = [(('object', 'builtins'), -1)]
        else:
            extra = []
        c = Classic()
        v = version_registry.get_version(c)
        res = extra + [(('Classic', __name__), 0)]
        self.assertEqual(v, res)
        state = state_pickler.get_state(c)
        self.assertEqual(state.__metadata__['version'], res)

        n = New()
        v = version_registry.get_version(n)
        res = extra + [(('New', __name__), 0)]
        self.assertEqual(v, res)
        state = state_pickler.get_state(n)
        self.assertEqual(state.__metadata__['version'], res)

        t = TraitClass()
        v = version_registry.get_version(t)
        res = extra + [(('CHasTraits', 'traits.ctraits'), -1),
               (('HasTraits', 'traits.has_traits'), -1),
               (('TraitClass', __name__), 0)]
        self.assertEqual(v, res)
        state = state_pickler.get_state(t)
        self.assertEqual(state.__metadata__['version'], res)

    def test_reload(self):
        """Test if the registry is reload safe."""
        # A dummy handler.
        def h(x, y):
            pass

        registry = version_registry.registry
        registry.register('A', __name__, h)
        self.assertEqual(registry.handlers.get(('A', __name__)), h)
        reload(version_registry)
        registry = version_registry.registry
        self.assertEqual(registry.handlers.get(('A', __name__)), h)
        del registry.handlers[('A', __name__)]
        self.assertFalse(('A', __name__) in registry.handlers)

    def test_update(self):
        """Test if update method calls the handlers in order."""
        registry = version_registry.registry

        # First an elementary test.
        c = Classic()
        state = state_pickler.get_state(c)
        h = Handler()
        registry.register('Classic', __name__, h.upgrade)
        c1 = state_pickler.create_instance(state)
        state_pickler.set_state(c1, state)
        self.assertEqual(h.calls, [('upgrade', state, 0)])
        # Remove the handler.
        registry.unregister('Classic', __name__)

        # Now check to see if this works for inheritance trees.
        t = Test()
        state = state_pickler.get_state(t)
        h = Handler()
        registry.register('Classic', __name__, h.upgrade)
        registry.register('New', __name__, h.upgrade)
        registry.register('Test', __name__, h.upgrade1)
        t1 = state_pickler.create_instance(state)
        state_pickler.set_state(t1, state)
        # This should call New handler, then the Test and then
        # Classic.
        self.assertEqual(h.calls, [('upgrade', state, 0),
                                   ('upgrade1', state, 1),
                                   ('upgrade', state.a, 0)])



if __name__ == "__main__":
    unittest.main()
