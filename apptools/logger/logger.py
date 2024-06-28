# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Convenience functions for creating logging handlers etc. """


# Standard library imports.
import logging
from logging.handlers import RotatingFileHandler

# Local imports.
from .log_queue_handler import LogQueueHandler


# The default logging level.
LEVEL = logging.DEBUG

# The default formatter.
FORMATTER = logging.Formatter("%(levelname)s|%(asctime)s|%(message)s")


class LogFileHandler(RotatingFileHandler):
    """The default log file handler."""

    def __init__(
        self,
        path,
        mode="a",
        maxBytes=1000000,
        backupCount=3,
        level=None,
        formatter=None,
        encoding=None,
        delay=False,
    ):
        RotatingFileHandler.__init__(
            self,
            filename=path,
            mode=mode,
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding=encoding,
            delay=delay,
        )

        if level is None:
            level = LEVEL
        if formatter is None:
            formatter = FORMATTER
        # Set our default formatter and log level.
        self.setFormatter(formatter)
        self.setLevel(level)


def add_log_queue_handler(logger, level=None, formatter=None):
    """Adds a queueing log handler to a logger."""
    if level is None:
        level = LEVEL
    if formatter is None:
        formatter = FORMATTER

    # Add the handler to the root logger.
    log_queue_handler = LogQueueHandler()
    log_queue_handler.setLevel(level)
    log_queue_handler.setFormatter(formatter)
    logger.addHandler(log_queue_handler)
    return log_queue_handler
