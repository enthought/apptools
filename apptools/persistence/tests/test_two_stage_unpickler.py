# -----------------------------------------------------------------------------
#
#  Copyright (c) 2008 by Enthought, Inc.
#  All rights reserved.
#
#  Author: Dave Peterson <dpeterson@enthought.com>
#          Prabhu Ramachandran <prabhu@aero.iitb.ac.in>
# -----------------------------------------------------------------------------

""" This was previously a test for the now deleted apptools.sweet_pickle
sub package.  It is included here to showcase how apptools.persistance can be
used to replace sweet_pickle functionality.
"""

import io
import random
import re
import pickle
import unittest

from apptools.persistence.versioned_unpickler import VersionedUnpickler

########################################


# Usecase1: generic case
class A(object):
    def __init__(self, b=None):
        self.x = 0
        self.set_b(b)

    def set_b(self, b):
        self.b_ref = b
        if b and hasattr(b, "y"):
            self.x = b.y

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.set_b(self.b_ref)

    def __initialize__(self):
        while self.b_ref is None and self.b_ref.y != 0:
            yield True
        self.set_b(self.b_ref)


class B(object):
    def __init__(self, a=None):
        self.y = 0
        self.set_a(a)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["y"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.set_a(self.a_ref)

    def set_a(self, a):
        self.a_ref = a
        if a and hasattr(a, "x"):
            self.y = a.x

    def __initialize__(self):
        while self.a_ref is None and self.a_ref.x != 0:
            yield True
        self.set_a(self.a_ref)


class GenericTestCase(unittest.TestCase):
    def test_generic(self):
        a = A()
        b = B()
        a.x = random.randint(1, 100)
        b.set_a(a)
        a.set_b(b)
        value = a.x

        # This will fail, even though we have a __setstate__ method.
        s = pickle.dumps(a)
        new_a = pickle.loads(s)
        try:
            new_a.x
            new_a.b_ref.y
        except Exception:
            pass

        # This will work!
        s = pickle.dumps(a)
        new_a = VersionedUnpickler(io.BytesIO(s)).load()
        assert new_a.x == new_a.b_ref.y == value


########################################
# Usecase2: Toy Application


class StringFinder(object):
    def __init__(self, source, pattern):
        self.pattern = pattern
        self.source = source
        self.data = []

    def __getstate__(self):
        s = self.__dict__.copy()
        del s["data"]
        return s

    def __initialize__(self):
        while not self.source.initialized:
            yield True
        self.find()

    def find(self):
        pattern = self.pattern
        string = self.source.data
        self.data = [
            (x.start(), x.end()) for x in re.finditer(pattern, string)
        ]


class XMLFileReader(object):
    def __init__(self, file_name):
        self.data = ""
        self.initialized = False
        self.file_name = file_name
        self.read()

    def __getstate__(self):
        s = self.__dict__.copy()
        del s["data"]
        del s["initialized"]
        return s

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.read()

    def read(self):
        # Make up random data from the filename
        data = [10 * x for x in self.file_name]
        random.shuffle(data)
        self.data = " ".join(data)
        self.initialized = True


class Application(object):
    def __init__(self):
        self.reader = XMLFileReader("some_test_file.xml")
        self.finder = StringFinder(self.reader, "e")

    def get(self):
        pass


class ToyAppTestCase(unittest.TestCase):
    def test_toy_app(self):
        a = Application()
        a.finder.find()
        a.get()
        s = pickle.dumps(a)
        b = pickle.loads(s)
        # Won't work.
        try:
            b.get()
        except Exception:
            pass

        # Works fine.
        c = VersionedUnpickler(io.BytesIO(s)).load()
        c.get()
