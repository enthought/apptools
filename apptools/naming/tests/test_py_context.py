# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Tests the Python namespace context. """


# Enthought library imports.
from apptools.naming.api import PyContext

# Local imports.
from .test_context import ContextTestCase


class PyContextTestCase(ContextTestCase):
    """ Tests the Python namespace context. """

    ###########################################################################
    # 'ContextTestCase' interface.
    ###########################################################################

    def create_context(self):
        """ Creates the context that we are testing. """

        return PyContext(namespace={})
