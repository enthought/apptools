# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest


class TestDeprecated(unittest.TestCase):

    def test_undo_deprecated(self):
        warn_msg = ("apptools.undo is deprecated and will be removed in a "
        "future release. The functionality is now available via pyface.undo")
        with self.assertWarns(DeprecationWarning, msg=warn_msg):
            import apptools.undo.api

        with self.assertWarns(DeprecationWarning, msg=warn_msg):
            import apptools.undo.action.api
