#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
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


# Enthought library imports.
from traits.etsconfig.api import ETSConfig
from traitsui.api import Handler

# Local imports.
from .adapter_base import AdapterBase
from .package_globals import get_permissions_manager


# Register the bundled adapters.
from .adapters import pyface_action

if ETSConfig.toolkit == 'wx':
    from .adapters import wx_window
elif ETSConfig.toolkit == 'qt4':
    from .adapters import qt4_widget


class SecureProxy(object):
    """The SecureProxy class is a wrapper for an object whose enabled and
    visible states can be managed.  It attaches one or more permissions to the
    object and enables and shows the object only if those permissions allow it.
    In all other respects it behaves exactly like the object.  It is based on
    Tomer Filiba's Object Proxy cookbook recipe."""

    __slots__ = ('_ets', '__weakref__')

    def __init__(self, proxied, permissions, show=True):
        """Initialise the instance.  proxied is the object whose enabled and
        visible states are managed according to the permissions of the current
        user.  permissions is a list of permissions to attach to the object.
        show is set if the proxied object should be visible when it is
        disabled."""

        adapter = object.__getattribute__(self, '_ets')

        # Correct the current values.
        if not show:
            adapter.update_visible(adapter.get_visible())

        adapter.update_enabled(adapter.get_enabled())

    # Proxying (special cases).
    def __getattribute__(self, name):
        return getattr(object.__getattribute__(self, '_ets').proxied, name)

    def __delattr__(self, name):
        delattr(object.__getattribute__(self, '_ets').proxied, name)

    def __setattr__(self, name, value):
        object.__getattribute__(self, '_ets').setattr(name, value)

    def __nonzero__(self):
        return bool(object.__getattribute__(self, '_ets').proxied)

    def __str__(self):
        return str(object.__getattribute__(self, '_ets').proxied)

    def __repr__(self):
        return repr(object.__getattribute__(self, '_ets').proxied)

    # Factories.
    _special_names = [
        '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__',
        '__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__',
        '__eq__', '__float__', '__floordiv__', '__ge__', '__getitem__',
        '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__',
        '__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__',
        '__imul__', '__int__', '__invert__', '__ior__', '__ipow__',
        '__irshift__', '__isub__', '__iter__', '__itruediv__', '__ixor__',
        '__le__', '__len__', '__long__', '__lshift__', '__lt__', '__mod__',
        '__mul__', '__ne__', '__neg__', '__oct__', '__or__', '__pos__',
        '__pow__', '__radd__', '__rand__', '__rdiv__', '__rdivmod__',
        '__reduce__', '__reduce_ex__', '__repr__', '__reversed__',
        '__rfloorfiv__', '__rlshift__', '__rmod__', '__rmul__', '__ror__',
        '__rpow__', '__rrshift__', '__rshift__', '__rsub__', '__rtruediv__',
        '__rxor__', '__setitem__', '__setslice__', '__sub__', '__truediv__',
        '__xor__', 'next',
    ]

    @classmethod
    def _ets_class_proxy(cls, theclass):
        """Creates a proxy for the given class."""

        def make_method(name):
            def method(self, *args, **kw):
                return getattr(object.__getattribute__(self, '_ets').proxied, name)(*args, **kw)
            return method

        namespace = {}
        for name in cls._special_names:
            if hasattr(theclass, name) and not hasattr(cls, name):
                namespace[name] = make_method(name)

        return type("%s(%s)" % (cls.__name__, theclass.__name__), (cls,),
                namespace)

    def __new__(cls, proxied, permissions, show=True):
        """Apply a set of permissions to an object.  This may be done by
        creating a proxy or by modifying the object in situ depending on its
        type.
        """

        # Create the adapter.
        adapter = AdapterBase.factory(proxied, permissions, show)

        # Try and adapt the object itself.
        adapted = adapter.adapt()

        if adapted is None:
            # Create a wrapper for the object.  The cache is unique per
            # deriving class to ensure there are no clashes with any
            # sub-classes with the same name.
            try:
                cache = cls.__dict__['_ets_cache']
            except KeyError:
                cls._ets_cache = cache = {}

            pclass = proxied.__class__
            try:
                theclass = cache[pclass]
            except KeyError:
                cache[pclass] = theclass = cls._ets_class_proxy(pclass)

            adapted = object.__new__(theclass)

            # Save the adapter in the adapted object.
            object.__setattr__(adapted, '_ets', adapter)
        else:
            # Correct the current values.
            if not show:
                adapter.update_visible(adapter.get_visible())

            adapter.update_enabled(adapter.get_enabled())

            # Save the adapter in the adapted object.
            adapted._ets = adapter

        return adapted


class SecureHandler(Handler):
    """The SecureHandler class is a sub-class of the TraitsUI Handler class
    that ensures that the enabled and visible state of the items of a TraitsUI
    view are updated when the user's authorisation state changes.
    """

    def __init__(self, **traits):
        """Initialise the object."""

        super(SecureHandler, self).__init__(**traits)

        get_permissions_manager().user_manager.on_trait_event(self._refresh,
                'user_authenticated')

    def init_info(self, info):
        """Reimplemented to save the UIInfo object."""

        self._info = info

    def _refresh(self):
        """Invoked whenever the current user's authorisation state changes."""

        # FIXME: This is (currently) an internal method.
        self._info.ui._evaluate_when()
