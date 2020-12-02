# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# Standard library imports.
from logging import Handler

# Local imports.
from .ring_buffer import RingBuffer


class LogQueueHandler(Handler):

    """Buffers up the log messages so that we can display them later.
    This is important on startup when log messages are generated before
    the ui has started.  By putting them in this queue we can display
    them once the ui is ready.
    """

    # The view where updates will go
    _view = None

    def __init__(self, size=1000):
        Handler.__init__(self)
        # only buffer 1000 log records
        self.size = size
        self.ring = RingBuffer(self.size)
        self.dirty = False

    def emit(self, record):
        """ Actually this is more like an enqueue than an emit()."""
        self.ring.append(record)
        if self._view is not None:
            try:
                self._view.update()
            except Exception:
                pass
        self.dirty = True

    def get(self):
        self.dirty = False

        try:
            result = self.ring.get()
        except Exception:
            # we did our best and it won't cause too much damage
            # to just return a bogus message
            result = []

        return result

    def has_new_records(self):
        return self.dirty

    def reset(self):
        # start over with a new empty buffer
        self.ring = RingBuffer(self.size)
        if self._view is not None:
            try:
                self._view.update()
            except Exception:
                pass
        self.dirty = True
