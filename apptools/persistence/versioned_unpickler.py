# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
# Standard library imports
from pickle import _Unpickler as Unpickler
from pickle import UnpicklingError, BUILD
import logging
from types import GeneratorType

# Enthought library imports
from apptools.persistence.updater import __replacement_setstate__


logger = logging.getLogger(__name__)


##############################################################################
# class 'NewUnpickler'
##############################################################################
class NewUnpickler(Unpickler):
    """An unpickler that implements a two-stage pickling process to make it
    possible to unpickle complicated Python object hierarchies where the
    unserialized state of an object depends on the state of other objects in
    the same pickle.
    """

    def load(self, max_pass=-1):
        """Read a pickled object representation from the open file.

        Return the reconstituted object hierarchy specified in the file.
        """
        # List of objects to be unpickled.
        self.objects = []

        # We overload the load_build method.
        dispatch = self.dispatch
        dispatch[BUILD[0]] = NewUnpickler.load_build

        # call the super class' method.
        ret = Unpickler.load(self)
        self.initialize(max_pass)
        self.objects = []

        # Reset the Unpickler's dispatch table.
        dispatch[BUILD[0]] = Unpickler.load_build
        return ret

    def initialize(self, max_pass):
        # List of (object, generator) tuples that initialize objects.
        generators = []

        # Execute object's initialize to setup the generators.
        for obj in self.objects:
            if hasattr(obj, "__initialize__") and callable(obj.__initialize__):
                ret = obj.__initialize__()
                if isinstance(ret, GeneratorType):
                    generators.append((obj, ret))
                elif ret is not None:
                    raise UnpicklingError(
                        "Unexpected return value from "
                        "__initialize__.  %s returned %s" % (obj, ret)
                    )

        # Ensure a maximum number of passes
        if max_pass < 0:
            max_pass = len(generators)

        # Now run the generators.
        count = 0
        while len(generators) > 0:
            count += 1
            if count > max_pass:
                not_done = [x[0] for x in generators]
                msg = """Reached maximum pass count %s.  You may have
                         a deadlock!  The following objects are
                         uninitialized: %s""" % (
                    max_pass,
                    not_done,
                )
                raise UnpicklingError(msg)
            for o, g in generators[:]:
                try:
                    next(g)
                except StopIteration:
                    generators.remove((o, g))

    # Make this a class method since dispatch is a class variable.
    # Otherwise, supposing the initial VersionedUnpickler.load call (which
    # would have overloaded the load_build method) makes a pickle.load call at
    # some point, we would have the dispatch still pointing to
    # NewPickler.load_build whereas the object being passed in will be an
    # Unpickler instance, causing a TypeError.
    def load_build(cls, obj):
        # Just save the instance in the list of objects.
        if isinstance(obj, NewUnpickler):
            obj.objects.append(obj.stack[-2])
        Unpickler.load_build(obj)

    load_build = classmethod(load_build)


class VersionedUnpickler(NewUnpickler):
    """This class reads in a pickled file created at revision version 'n'
    and then applies the transforms specified in the updater class to
    generate a new set of objects which are at revision version 'n+1'.

    I decided to keep the loading of the updater out of this generic class
    because we will want updaters to be generated for each plugin's type
    of project.

    This ensures that the VersionedUnpickler can remain ignorant about the
    actual version numbers - all it needs to do is upgrade one release.
    """

    def __init__(self, file, updater=None):
        Unpickler.__init__(self, file)
        self.updater = updater

    def find_class(self, module, name):
        """Overridden method from Unpickler.

        NB  __setstate__ is not called until later.
        """

        if self.updater:
            # check to see if this class needs to be mapped to a new class
            # or module name
            original_module, original_name = module, name
            module, name = self.updater.get_latest(module, name)

            # load the class...
            klass = self.import_name(module, name)

            # add the updater....  TODO - why the old name?
            self.add_updater(original_module, original_name, klass)

        else:
            # there is no updater so we will be reading in an up to date
            # version of the file...
            try:
                klass = Unpickler.find_class(self, module, name)
            except Exception:
                logger.error("Looking for [%s] [%s]" % (module, name))
                logger.exception(
                    "Problem using default unpickle functionality"
                )

            # restore the original __setstate__ if necessary
            fn = getattr(klass, "__setstate_original__", False)
            if fn:
                setattr(klass, "__setstate__", fn)

        return klass

    def add_updater(self, module, name, klass):
        """If there is an updater defined for this class we will add it to the
        class as the __setstate__ method.
        """

        fn = self.updater.setstates.get((module, name), False)

        if fn:
            # move the existing __setstate__ out of the way
            self.backup_setstate(module, klass)

            # add the updater into the class
            setattr(klass, "__updater__", fn)

            # hook up our __setstate__ which updates self.__dict__
            setattr(klass, "__setstate__", __replacement_setstate__)

        else:
            pass

    def backup_setstate(self, module, klass):
        """If the class has a user defined __setstate__ we back it up."""
        if getattr(klass, "__setstate__", False):

            if getattr(klass, "__setstate_original__", False):
                # don't overwrite the original __setstate__
                name = "__setstate__%s" % self.updater.__class__
            else:
                # backup the original __setstate__ which we will restore
                # and run later when we have finished updating the class
                name = "__setstate_original__"

            method = getattr(klass, "__setstate__")
            setattr(klass, name, method)

        else:
            # the class has no __setstate__ method so do nothing
            pass

    def import_name(self, module, name):
        """
        If the class is needed for the latest version of the application then
        it should presumably exist.

        If the class no longer exists then we should perhaps return
        a proxy of the class.

        If the persisted file is at v1 say and the application is at v3 then
        objects that are required for v1 and v2 do not have to exist they only
        need to be placeholders for the state during an upgrade.
        """
        module = __import__(module, globals(), locals(), [name])
        return vars(module)[name]
