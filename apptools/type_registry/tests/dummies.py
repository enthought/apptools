# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
import abc


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


class Abstract(metaclass=abc.ABCMeta):
    pass


class Concrete(object):
    pass


class ConcreteSubclass(Concrete):
    pass


for typ in (A, B, C, D, Mixed, Abstract, Concrete, ConcreteSubclass):
    typ.__module__ = "dummies"


Abstract.register(Concrete)
