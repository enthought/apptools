# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" A reference to an object that lives outside of the naming system. """


# Enthought library imports.
from traits.api import HasPrivateTraits, List, Str

# Local imports.
from .address import Address


class Reference(HasPrivateTraits):
    """A reference to an object that lives outside of the naming system.

    References provide a way to store the address(s) of objects that live
    outside of the naming system.  A reference consists of a list of
    addresses that represent a communications endpoint for the object being
    referenced.

    A reference also contains information to assist in the creation of an
    instance of the object to which it refers.  It contains the name of
    the class that will be created and the class name and location of a
    factory that will be used to do the actual instance creation.

    """

    #### 'Reference' interface ################################################

    # The list of addresses that can be used to 'contact' the object.
    addresses = List(Address)

    # The class name of the object that this reference refers to.
    class_name = Str

    # The class name of the object factory.
    factory_class_name = Str
