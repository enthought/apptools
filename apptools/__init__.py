# Copyright (c) 2007-2014 by Enthought, Inc.
# All rights reserved.

from __future__ import absolute_import
try:
    from apptools._version import full_version as __version__
except ImportError:
    __version__ = 'not-built'

__requires__ = [
    'traitsui',
    'configobj',
]
