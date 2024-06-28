# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" The representation of a name-to-object binding in a context. """


# Enthought libary imports.
from traits.api import Any, HasTraits, Property, Str


class Binding(HasTraits):
    """ The representation of a name-to-object binding in a context. """

    #### 'Binding' interface ##################################################

    # The class name of the object bound to the name in the binding.
    class_name = Property(Str)

    # The name.
    name = Str

    # The object bound to the name in the binding.
    obj = Any

    #### Experimental 'Binding' interface #####################################

    # fixme: These is not part of the JNDI spec, but they do seem startlingly
    # useful!
    #
    # fixme: And, errr, startlingly broken! If the context that the binding
    # is in is required then just look up the name minus the last component!
    #
    # The context that the binding came from.
    context = Any

    # The name of the bound object within the namespace.
    namespace_name = Property(Str)

    #### 'Private' interface ##################################################

    # Shadow trait for the 'class_name' property.
    _class_name = Str

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __str__(self):
        """ Returns an informal string representation of the object. """

        return super(Binding, self).__str__() + "(name=%s, obj=%s)" % (
            self.name,
            self.obj,
        )

    ###########################################################################
    # 'Binding' interface.
    ###########################################################################

    #### Properties ###########################################################

    # class_name
    def _get_class_name(self):
        """ Returns the class name of the object. """

        if len(self._class_name) == 0:
            if self.obj is None:
                class_name = None

            else:
                klass = self.obj.__class__

                class_name = "%s.%s" % (klass.__module__, klass.__name__)

        return class_name

    def _set_class_name(self, class_name):
        """ Sets the class name of the object. """

        self._class_name = class_name

    # namespace_name
    def _get_namespace_name(self):
        """ Returns the name of the context within its own namespace. """

        if self.context is not None:
            base = self.context.namespace_name

        else:
            base = ""

        if len(base) > 0:
            namespace_name = base + "/" + self.name

        else:
            namespace_name = self.name

        return namespace_name
