#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint

from traits.api import Bool, Dict, HasTraits, Instance, Int, List, Set, Str, \
    Tuple

import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8.8s [%(name)s:%(lineno)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level='INFO')
logger = logging.getLogger(__name__)


class Generic(HasTraits):
    # uuid = Instance(uuid.UUID, factory=uuid.uuid4)
    int_ = Int
    str_ = Str
    list_ = List
    dict_ = Dict
    tuple_ = Tuple
    set_ = Set
    bool_ = Bool
    child_ = Instance(HasTraits)

    def __eq__(self, other):
        if not hasattr(other, 'get'):
            return False
        # pprint(zip(sorted(self.get().items()),
                   # sorted(other.get().items())))
        return self.get() == other.get()

    def __ne__(self, other):
        if not hasattr(other, 'get'):
            return True
        # pprint(zip(sorted(self.get().items()),
                   # sorted(other.get().items())))
        return self.get() != other.get()


TEST_LIST = [1, 2, set(), "X"]
TEST_DICT = {'a': 0, 'b': {}, 'c': ()}
TEST_TUPLE = ((), {}, [4], ([set([])],), "banana", 59, u"foo", 5.3)
TEST_SET = set(['a', 1, "x93"])
TEST_ATTRS = {'int_': 5,
              'str_': "test string",
              'list_': TEST_LIST,
              'dict_': TEST_DICT,
              'tuple_': TEST_TUPLE,
              'set_': TEST_SET,
              'bool_': True}
