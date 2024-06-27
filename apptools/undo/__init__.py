# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Supports undoing and scripting application commands.
    Part of the AppTools project of the Enthought Tool Suite.
"""
import warnings

warnings.warn(
    ("apptools.undo is deprecated and will be removed in a future release. The"
     " functionality is now available via pyface.undo"),
    DeprecationWarning,
    stacklevel=2
)
