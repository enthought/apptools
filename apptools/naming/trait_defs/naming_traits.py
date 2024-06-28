# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# -------------------------------------------------------------------------------
#  Imports:
# -------------------------------------------------------------------------------

import sys

from traits.api import Trait, TraitHandler, TraitFactory

from traits.trait_base import class_of, get_module_name

from apptools.naming.api import Binding


# -------------------------------------------------------------------------------
#  'NamingInstance' trait factory:
# -------------------------------------------------------------------------------


def NamingInstance(klass=None, value="", allow_none=False, **metadata):
    metadata.setdefault("copy", "deep")
    return Trait(
        value,
        NamingTraitHandler(
            klass, or_none=allow_none, module=get_module_name()
        ),
        **metadata
    )


NamingInstance = TraitFactory(NamingInstance)

# -------------------------------------------------------------------------------
#  'NamingTraitHandler' class:
# -------------------------------------------------------------------------------


class NamingTraitHandler(TraitHandler):

    # ---------------------------------------------------------------------------
    #  Initializes the object:
    # ---------------------------------------------------------------------------

    def __init__(self, aClass, or_none, module):
        """Initializes the object."""
        self.or_none = or_none is not False
        self.module = module
        self.aClass = aClass
        if (aClass is not None) and (
            not isinstance(aClass, (str, type))
        ):
            self.aClass = aClass.__class__

    def validate(self, object, name, value):
        if isinstance(value, str):
            if value == "":
                if self.or_none:
                    return ""
                else:
                    self.validate_failed(object, name, value)
            try:
                value = self._get_binding_for(value)
            except:  # noqa: E722
                self.validate_failed(object, name, value)

        if isinstance(self.aClass, str):
            self.resolve_class(object, name, value)

        if isinstance(value, Binding) and (
            (self.aClass is None) or isinstance(value.obj, self.aClass)
        ):
            return value.namespace_name
        self.validate_failed(object, name, value)

    def info(self):
        aClass = self.aClass
        if aClass is None:
            result = "path"
        else:
            if type(aClass) is not str:
                aClass = aClass.__name__
            result = "path to an instance of " + class_of(aClass)
        if self.or_none is None:
            return result + " or an empty string"
        return result

    def validate_failed(self, object, name, value):
        if not isinstance(value, type):
            msg = "class %s" % value.__class__.__name__
        else:
            msg = "%s (i.e. %s)" % (str(type(value))[1:-1], repr(value))
        self.error(object, name, msg)

    def get_editor(self, trait):
        if self.editor is None:
            from traitsui.api import DropEditor

            self.editor = DropEditor(
                klass=self.aClass, binding=True, readonly=False
            )
        return self.editor

    def post_setattr(self, object, name, value):
        other = None
        if value != "":
            other = self._get_binding_for(value).obj
        object.__dict__[name + "_"] = other

    def _get_binding_for(self, value):

        result = None

        # FIXME: The following code makes this whole component have a
        # dependency on envisage, and worse, assumes the use of a particular
        # project plugin!  This is horrible and should be refactored out,
        # possibly to a custom sub-class of whoever needs this behavior.
        try:
            from envisage import get_application

            workspace = get_application().service_registry.get_service(
                "envisage.project.IWorkspace"
            )
            result = workspace.lookup_binding(value)
        except ImportError:
            pass

        return result

    def resolve_class(self, object, name, value):
        aClass = self.find_class()
        if aClass is None:
            self.validate_failed(object, name, value)
        self.aClass = aClass

        # fixme: The following is quite ugly, because it wants to try and fix
        # the trait referencing this handler to use the 'fast path' now that
        # the actual class has been resolved. The problem is finding the trait,
        # especially in the case of List(Instance('foo')), where the
        # object.base_trait(...) value is the List trait, not the Instance
        # trait, so we need to check for this and pull out the List
        # 'item_trait'. Obviously this does not extend well to other traits
        # containing nested trait references (Dict?)...
        trait = object.base_trait(name)
        handler = trait.handler
        if (handler is not self) and hasattr(handler, "item_trait"):
            trait = handler.item_trait
        trait.validate(self.fast_validate)

    def find_class(self):
        module = self.module
        aClass = self.aClass
        col = aClass.rfind(".")
        if col >= 0:
            module = aClass[:col]
            aClass = aClass[col + 1:]
        theClass = getattr(sys.modules.get(module), aClass, None)
        if (theClass is None) and (col >= 0):
            try:
                theClass = getattr(__import__(module), aClass, None)
            except Exception:
                pass
        return theClass
