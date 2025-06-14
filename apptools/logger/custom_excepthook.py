# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


# Standard library imports.
import logging
from traceback import format_exception


"""
    To catch exceptions with our own code this code needs to be added
    sys.excepthook = custom_excepthook
"""


def custom_excepthook(type, value, traceback):
    """ Pass on the exception to the logging system. """

    msg = "Custom - Traceback (most recent call last):\n"
    list = format_exception(type, value, traceback)

    msg = "".join(list)

    # Try to find the module that the exception actually came from.
    name = getattr(traceback.tb_frame, "f_globals", {}).get(
        "__name__", __name__
    )
    logger = logging.getLogger(name)
    logger.error(msg)
