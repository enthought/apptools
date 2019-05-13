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
# Description: <Enthought application scripting package component>
#------------------------------------------------------------------------------


# Enthought library imports.
from traits.api import Any, Callable, HasTraits

# Local imports.
from .bind_event import BindEvent
from .package_globals import get_script_manager
from .scriptable_type import make_object_scriptable


class FactoryWrapper(HasTraits):
    """The FactoryWrapper class wraps a factory for an object."""

    #### 'FactoryWrapper' interface ###########################################

    # The optional object that defines the scripting API.
    api = Any

    # The object factory.
    factory = Callable

    # The optional attribute include list.
    includes = Any

    # The optional attribute exclude list.
    excludes = Any

    ###########################################################################
    # 'FactoryWrapper' interface.
    ###########################################################################

    def create_scriptable_object(self, name):
        """Invoke the factory to create the object then make it scriptable."""

        obj = self.factory()

        sm = get_script_manager()
        sm.bind_event = BindEvent(name=name, obj=obj)

        make_object_scriptable(obj, self.api, self.includes, self.excludes)

        return obj


class _LazyNode(object):
    """The _LazyNode class implements a node in a lazy namespace that will
    automatically invoke a factory if one is referenced."""

    def __getattribute__(self, name):

        value = super(_LazyNode, self).__getattribute__(name)

        if isinstance(value, FactoryWrapper):
            value = value.create_scriptable_object(name)
            setattr(self, name, value)

        return value


class LazyNamespace(dict):
    """The LazyNamespace class implements a lazy namespace that will
    automatically invoke a factory if one is referenced."""

    def __getitem__(self, name):

        value = super(LazyNamespace, self).__getitem__(name)

        if isinstance(value, FactoryWrapper):
            value = value.create_scriptable_object(name)
            self[name] = value

        return value


def add_to_namespace(so, name, nspace):
    """Add a named scriptable object (or a factory for one) to a lazy
    namespace.  If a name is a dotted name then intermediary nodes in the
    namespace are created as required."""

    def save_obj(obj, name):

        if isinstance(nspace, LazyNamespace):
            nspace[name] = obj
        else:
            setattr(nspace, name, obj)

    parts = name.split('.')

    for part in parts[:-1]:
        if isinstance(nspace, LazyNamespace):
            try:
                next_nspace = nspace[part]
            except KeyError:
                next_nspace = _LazyNode()
        elif isinstance(nspace, _LazyNode):
            try:
                next_nspace = nspace[part]
            except KeyError:
                next_nspace = _LazyNode()
        else:
            raise NameError

        save_obj(next_nspace, part)
        nspace = next_nspace

    if not isinstance(nspace, (LazyNamespace, _LazyNode)):
        raise NameError

    save_obj(so, parts[-1])
