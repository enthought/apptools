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
""" The base class for all directory contexts. """


# Enthought library imports.
from traits.api import Dict

# Local imports.
from .context import Context
from .exception import NameNotFoundError, NotContextError


class DirContext(Context):
    """ The base class for all directory contexts. """

    # The attributes of every object in the context.  The attributes for the
    # context itself have the empty string as the key.
    #
    # {str name : dict attributes}
    _attributes = Dict

    ###########################################################################
    # 'DirContext' interface.
    ###########################################################################

    def get_attributes(self, name):
        """ Returns the attributes associated with a named object. """

        # If the name is empty then we return the attributes of this context.
        if len(name) == 0:
            attributes = self._get_attributes(name)

        else:
            # Parse the name.
            components = self._parse_name(name)

            # If there is exactly one component in the name then the operation
            # takes place in this context.
            if len(components) == 1:
                atom = components[0]

                if not self._is_bound(atom):
                    raise NameNotFoundError(name)

                # Do the actual get.
                attributes = self._get_attributes(atom)

            # Otherwise, attempt to continue resolution into the next context.
            else:
                if not self._is_bound(components[0]):
                    raise NameNotFoundError(components[0])

                next_context = self._get_next_context(components[0])
                attributes = next_context.get_attributes(
                    '/'.join(components[1:]))

        return attributes

    def set_attributes(self, name, attributes):
        """ Sets the attributes associated with a named object. """

        # If the name is empty then we set the attributes of this context.
        if len(name) == 0:
            attributes = self._set_attributes(name, attributes)

        else:
            # Parse the name.
            components = self._parse_name(name)

            # If there is exactly one component in the name then the operation
            # takes place in this context.
            if len(components) == 1:
                atom = components[0]

                if not self._is_bound(atom):
                    raise NameNotFoundError(name)

                # Do the actual set.
                self._set_attributes(atom, attributes)

            # Otherwise, attempt to continue resolution into the next context.
            else:
                if not self._is_bound(components[0]):
                    raise NameNotFoundError(components[0])

                next_context = self._get_next_context(components[0])
                next_context.set_attributes(
                    '/'.join(components[1:]), attributes
                )

        return

    # fixme: Non-JNDI
    def find_bindings(self, visitor):
        """ Find bindings with attributes matching criteria in visitor.

        Visitor is a function that is passed the bindings for each level of the
        heirarchy and the attribute dictionary for those bindings.  The visitor
        examines the bindings and dictionary and returns the bindings it is
        interested in.

        """

        bindings = visitor(self.list_bindings(), self._attributes)

        # recursively check other sub contexts.
        for binding in self.list_bindings():
            obj = binding.obj
            if isinstance(obj, DirContext):
                bindings.extend(obj.find_bindings(visitor))

        return bindings

    ###########################################################################
    # Protected 'DirContext' interface.
    ###########################################################################

    def _get_attributes(self, name):
        """ Returns the attributes of an object in this context. """

        attributes = self._attributes.setdefault(name, {})

        return attributes.copy()

    def _set_attributes(self, name, attributes):
        """ Sets the attributes of an object in this context. """

        self._attributes[name] = attributes

        return

    ###########################################################################
    # Protected 'Context' interface.
    ###########################################################################

    def _unbind(self, name):
        """ Unbinds a name from this context. """

        super(DirContext, self)._unbind(name)

        if name in self._attributes:
            del self._attributes[name]

        return

    def _rename(self, old_name, new_name):
        """ Renames an object in this context. """

        super(DirContext, self)._rename(old_name, new_name)

        if old_name in self._attributes:
            self._attributes[new_name] = self._attributes[old_name]
            del self._attributes[old_name]

        return

    def _destroy_subcontext(self, name):
        """ Destroys a sub-context of this context. """

        super(DirContext, self)._destroy_subcontext(name)

        if name in self._attributes:
            del self._attributes[name]

        return

#### EOF ######################################################################
