#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Riverbank Computing Limited
# Description: <Enthought permissions package component>
#------------------------------------------------------------------------------


# Standard library imports.
import os

# Enthought library imports.
from enthought.etsconfig.api import ETSConfig
from enthought.traits.api import HasTraits


class Persistent(HasTraits):
    """This is a base class that persists a Traits class to a file.  It is used
    by the default permissions policy and user manager to implement basic (ie.
    insecure) shared data storage.
    """

    def __init__(self, file_name, env_var_name, **traits):
        """Initialise the object.  file_name is the name of the file in the
        ETSConfig.application_home directory to persist the data to.
        env_var_name is the name of an environment variable that, if set, is
        used as the full path to the persisted data, overriding file_name."""

        super(Persistent, self).__init__(**traits)

        # Get the name of the file to use.
        fname = os.environ.get(env_var_name, None)

        if fname is None:
            fname = os.path.join(ETSConfig.application_home, file_name)

        self._fname = fname
