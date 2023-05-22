# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from pyface.base_toolkit import Toolkit
from pyface.toolkit import toolkit as pyface_toolkit

# Pyface will have selected the backend correctly by this point.
toolkit_name = pyface_toolkit.toolkit
# backwards compatibility
if toolkit_name == "qt4":
    toolkit_name = "qt"

toolkit = toolkit_object = Toolkit(
    "workbench",
    toolkit_name,
    f"apptools.workbench.ui.{toolkit_name}",
)
