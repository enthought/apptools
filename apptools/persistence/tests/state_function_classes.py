# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# Standard library imports
import logging

# Enthought library imports
from traits.api import Bool, Float, HasTraits, Int, Str


logger = logging.getLogger(__name__)


##############################################################################
# Classes to use within the tests
##############################################################################


class Foo(HasTraits):
    _enthought_pickle_version = Int(1)
    b1 = Bool(False)
    f1 = Float(1)
    i1 = Int(1)
    s1 = Str("foo")


class Bar(HasTraits):
    _enthought_pickle_version = Int(2)
    b2 = Bool(True)
    f2 = Float(2)
    i2 = Int(2)
    s2 = Str("bar")


class Baz(HasTraits):
    _enthought_pickle_version = Int(3)
    b3 = Bool(False)
    f3 = Float(3)
    i3 = Int(3)
    s3 = Str("baz")

    def __setstate__(self, state):
        logger.debug("Running Baz's original __setstate__")
        if state["_enthought_pickle_version"] < 3:
            info = [("b2", "b3"), ("f2", "f3"), ("i2", "i3"), ("s2", "s3")]
            for old, new in info:
                if old in state:
                    state[new] = state[old]
                    del state[old]
            state["_enthought_pickle_version"] = 3
        self.__dict__.update(state)
