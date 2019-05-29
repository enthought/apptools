#-----------------------------------------------------------------------------
#
#  Copyright (c) 2008 by Enthought, Inc.
#  All rights reserved.
#
#  Author: Dave Peterson <dpeterson@enthought.com>
#          Prabhu Ramachandran <prabhu@aero.iitb.ac.in>
#-----------------------------------------------------------------------------

# Test cases.
from __future__ import print_function
import random
import pickle
import apptools.sweet_pickle as sweet_pickle

########################################

# Usecase1: generic case
class A(object):
    def __init__(self, b=None):
        self.x = 0
        self.set_b(b)

    def set_b(self, b):
        self.b_ref = b
        if b and hasattr(b, 'y'):
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
        del state['y']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.set_a(self.a_ref)

    def set_a(self, a):
        self.a_ref = a
        if a and hasattr(a, 'x'):
            self.y = a.x

    def __initialize__(self):
        while self.a_ref is None and self.a_ref.x != 0:
            yield True
        self.set_a(self.a_ref)


def test_generic():
    print('\nRunning generic test...')

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
        print('\ta.x: %s' % new_a.x)
        print('\ta.b_ref.y: %s' % new_a.b_ref.y)
    except Exception as msg:
        print('\t%s' % 'Expected Error'.center(75,'*'))
        print('\t%s' % msg)
        print('\t%s' % ('*'*75))

    # This will work!
    s = pickle.dumps(a)
    new_a = sweet_pickle.loads(s)
    assert new_a.x == new_a.b_ref.y == value

    print('Generic test succesfull.\n\n')


########################################
# Usecase2: Toy Application
import re
class StringFinder(object):
    def __init__(self, source, pattern):
        self.pattern = pattern
        self.source = source
        self.data = []

    def __getstate__(self):
        s = self.__dict__.copy()
        del s['data']
        return s

    def __initialize__(self):
        while not self.source.initialized:
            yield True
        self.find()

    def find(self):
        pattern = self.pattern
        string = self.source.data
        self.data = [(x.start(), x.end()) for x in re.finditer(pattern, string)]


class XMLFileReader(object):
    def __init__(self, file_name):
        self.data = ''
        self.initialized = False
        self.file_name = file_name
        self.read()

    def __getstate__(self):
        s = self.__dict__.copy()
        del s['data']
        del s['initialized']
        return s

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.read()

    def read(self):
        # Make up random data from the filename
        data = [10*x for x in self.file_name]
        random.shuffle(data)
        self.data = ' '.join(data)
        self.initialized = True


class Application(object):
    def __init__(self):
        self.reader = XMLFileReader('some_test_file.xml')
        self.finder = StringFinder(self.reader, 'e')

    def get(self):
        print('\t%s' % self.finder.data)
        print('\t%s' % self.reader.data)


def test_toy_app():
    print('\nRunning toy app test...')

    a = Application()
    a.finder.find()
    a.get()
    s = pickle.dumps(a)
    b = pickle.loads(s)
    # Won't work.
    try:
        b.get()
    except Exception as msg:
        print('\t%s' % 'Expected Error'.center(75,'*'))
        print('\t%s' % msg)
        print('\t%s' % ('*'*75))

    # Works fine.
    c = sweet_pickle.loads(s)
    c.get()

    print('Toy app test succesfull.\n\n')


if __name__ == '__main__':
    test_generic()
    test_toy_app()
    print('ALL TESTS SUCCESFULL\n')
