#-----------------------------------------------------------------------------
#
#  Copyright (c) 2006 by Enthought, Inc.
#  All rights reserved.
#
#-----------------------------------------------------------------------------

""" Provider of a framework that dynamically determines the contents of a
    context at the time of interaction with the contents rather than at the
    time a class is written.

    This capability is particularly useful when the object acting as a context
    is part of a plug-in application -- such as Envisage.  In general, this
    capability allows the context to be:

    - Extendable by contributions from somewhere other than the original
      code writer
    - Dynamic in that the elements it is composed of can change each time
      someone interacts with the contents of the context.

    It should be noted that this capability is explicitly different from
    contexts that look at another container to determine their contents, such
    as a file system context!

    Users of this framework contribute items to a dynamic context by adding
    traits to the dynamic context instance.  (This addition can happen
    statically through the use of a Traits Category.)  The trait value is the
    context item's value and the trait definition's metadata determines how the
    item is treated within the context.  The support metadata is:

    context_name: A non-empty string
        Represents the name of the item within this context.  This must be
        present for the trait to show up as a context item though the value
        may change over time as the item gets bound to different names.
    context_order: A float value
        Indicates the position for the item within this context.  All
        dynamically contributed context items are sorted by ascending order
        of this value using the standard list sort function.
    is_context: A boolean value
        True if the item is itself a context.
"""

# Standardlibrary imports
import logging

# Local imports
from .binding import Binding
from .context import Context
from .exception import OperationNotSupportedError


# Setup a logger for this module.
logger = logging.getLogger(__name__)


class DynamicContext(Context):
    """ A framework that dynamically determines the contents of a context at
        the time of interaction with the contents rather than at the time a
        context class is written.

        It should be noted that this capability is explicitly different from
        contexts that look at another container to determine their contents,
        such as a file system context!
    """

    ##########################################################################
    # 'Context' interface.
    ##########################################################################

    ### protected interface ##################################################

    def _is_bound(self, name):
        """ Is a name bound in this context?
        """

        item = self._get_contributed_context_item(name)
        result = item != (None, None)

        return result


    def _is_context(self, name):
        """ Returns True if a name is bound to a context.
        """
        item = self._get_contributed_context_item(name)
        if item != (None, None):
            obj, trait = item
            result = True == trait.is_context
        else:
            result = False

        return result


    def _list_bindings(self):
        """ Lists the bindings in this context.
        """
        result = [ Binding(name=n, obj=o, context=self) for n, o, t in \
                self._get_contributed_context_items() ]

        return result


    def _list_names(self):
        """ Lists the names bound in this context.
        """
        result = [ n for n, o, t in self._get_contributed_context_items() ]

        return result


    def _lookup(self, name):
        """ Looks up a name in this context.
        """
        item = self._get_contributed_context_item(name)
        if item != (None, None):
            obj, trait = item
            result = obj
        else:
            result = None

        return result


    def _rename(self, old_name, new_name):
        """ Renames an object in this context.
        """

        item = self._get_contributed_context_item(old_name)
        if item != (None, None):
            obj, trait = item
            trait.context_name = new_name
        else:
            raise ValueError('Name "%s" not in context', old_name)


    def _unbind(self, name):
        """ Unbinds a name from this context.
        """
        # It is an error to try to unbind any contributed context items
        item = self._get_contributed_context_item(name)
        if item != (None, None):
            raise OperationNotSupportedError('Unable to unbind ' + \
                'built-in with name [%s]' % name)


    ##########################################################################
    # 'DynamicContext' interface.
    ##########################################################################

    ### protected interface ##################################################

    def _get_contributed_context_item(self, name):
        """ If the specified name matches a contributed context item then
            returns a tuple of the item's current value and trait definition
            (in that order.)  Otherwise, returns a tuple of (None, None).
        """
        result = (None, None)

        for n, o, t in self._get_contributed_context_items():
            if n == name:
                result = (o, t)

        return result


    def _get_contributed_context_items(self):
        """ Returns an ordered list of items to be treated as part of our
            context.

            Each item in the list is a tuple of its name, object, and trait
            definition (in that order.)
        """
        # Our traits that get treated as context items are those that declare
        # themselves via metadata on the trait definition.
        filter = {
            'context_name': lambda v: v is not None and len(v) > 0
            }
        traits = self.traits(**filter)

        # Sort the list of context items according to the name of the item.
        traits = [ (t.context_order, n, t) for n, t in traits.items() ]
        traits.sort()

        # Convert these trait definitions into a list of name and object tuples.
        result = [(t.context_name, getattr(self, n), t) for order, n, t \
            in traits]

        return result


### EOF ######################################################################

