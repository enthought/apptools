#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Enthought, Inc.
# Description: <Enthought naming package component>
#------------------------------------------------------------------------------
""" The base class for all context adapter factories. """


# Enthought library imports.
from apptools.type_manager.api import AdapterFactory

# Local imports.
from .context import Context


class ContextAdapterFactory(AdapterFactory):
    """ The base class for all context adapter factories. """

    #### 'AdapterFactory' interface ###########################################

    # The target class (the class that the factory can adapt objects to).
    target_class = Context

    ###########################################################################
    # Protected 'AbstractAdapterFactory' interface.
    ###########################################################################

    def _adapt(self, adaptee, target_class, environment, context):
        """ Returns an adapter that adapts an object to the target class. """

        adapter = self.adapter_class(
            adaptee=adaptee, environment=environment, context=context
        )

        return adapter

#### EOF ######################################################################
