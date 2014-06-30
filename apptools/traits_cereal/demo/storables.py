#!/usr/bin/env python
# -*- coding: utf-8 -*-

from traits.api import HasTraits, Int, Instance, List


class Child(HasTraits):
    """ Another class we would like to serialize/deserialize"""
    bar = Int


class Parent(HasTraits):
    """ A class we would like to serialize/deserialize"""
    child = Instance(Child)
    grandchildren = List

    def _grandchildren_default(self):
        return [{'booooh': 'baaaahhhh', 'child': self.child}]
