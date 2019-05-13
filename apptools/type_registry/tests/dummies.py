import abc

import six


class A(object):
    pass


class B(A):
    pass


class C(B):
    pass


class D(object):
    pass


class Mixed(A, D):
    pass


class Abstract(six.with_metaclass(abc.ABCMeta, object)):
    pass


class Concrete(object):
    pass


class ConcreteSubclass(Concrete):
    pass


for typ in (A, B, C, D, Mixed, Abstract, Concrete, ConcreteSubclass):
    typ.__module__ = 'dummies'


Abstract.register(Concrete)
