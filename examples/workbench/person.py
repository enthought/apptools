# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" A simple example of some object model. """


from traits.api import HasTraits, Int, Str


class Person(HasTraits):
    """A simple example of some object model!"""

    # Age in years.
    age = Int()

    # Name.
    name = Str()

    # ------------------------------------------------------------------------
    # 'object' interface.
    # ------------------------------------------------------------------------

    def __str__(self):
        """Return an informal string representation of the object."""

        return self.name
