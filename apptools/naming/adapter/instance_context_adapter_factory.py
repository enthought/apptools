""" Context adapter factory for Python instances. """


# Enthought library imports.
from apptools.naming.api import ContextAdapterFactory
from traits.api import List, Str
from apptools.type_manager import PythonObject

# Local imports.
from .instance_context_adapter import InstanceContextAdapter


class InstanceContextAdapterFactory(ContextAdapterFactory):
    """ Context adapter factoryfor Python instances. """

    #### 'ContextAdapterFactory' interface ####################################

    # The type of object that we adapt.
    adaptee_class = PythonObject

    #### 'InstanceContextAdapterFactory' interface ############################

    # By default every public attribute of an instance is exposed. Use the
    # following traits to either include or exclude attributes as appropriate.
    #
    # Regular expressions that describe the names of attributes to include.
    include = List(Str)

    # Regular expressions that describe the names of attributes to exclude.  By
    # default we exclude 'protected' and 'private' attributes and any
    # attributes that are artifacts of the traits mechanism.
    exclude = List(Str, ['_', 'trait_'])

    ###########################################################################
    # Protected 'AbstractAdapterFactory' interface.
    ###########################################################################

    def _adapt(self, adaptee, target_class, environment, context):
        """ Returns an adapter that adapts an object to the target class. """

        adapter = InstanceContextAdapter(
            adaptee     = adaptee,
            environment = environment,
            context     = context,
            include     = self.include,
            exclude     = self.exclude
        )

        return adapter

#### EOF ######################################################################
