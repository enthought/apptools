# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


"""
A re-usable method for calculating a unique name given a list of existing
names.

"""


def make_unique_name(base, existing=[], format="%s_%s"):
    """
    Return a name, unique within a context, based on the specified name.

    base: the desired base name of the generated unique name.
    existing: a sequence of the existing names to avoid returning.
    format: a formatting specification for how the name is made unique.

    """

    count = 2
    name = base
    while name in existing:
        name = format % (base, count)
        count += 1

    return name
