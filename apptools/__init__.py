# Copyright (c) 2007-2014 by Enthought, Inc.
# All rights reserved.

try:
    from apptools.version import version as __version__
except ImportError:
    # If we get here, we're using a source tree that hasn't been created via
    # the setup script.
    __version__ = "unknown"
