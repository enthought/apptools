""" The base class for adaptable objects. """


# Enthought library imports.
from traits.api import HasTraits, Instance

# Local imports.
from .adapter_manager import AdapterManager


class Adaptable(HasTraits):
    """ The base class for adaptable objects. """

    #### 'Adaptable' interface ################################################

    # The adapter manager in effect for the object.
    adapter_manager = Instance(AdapterManager)

    ###########################################################################
    # 'Adaptable' interface.
    ###########################################################################

    def adapt(self, target_class, *args, **kw):
        """ Returns True if the factory can produce an appropriate adapter. """

        if self.adapter_manager is not None:
            adapter = self.adapter_manager.adapt(
                self, target_class, *args, **kw
            )

        else:
            adapter = None

        return adapter

#### EOF ######################################################################
