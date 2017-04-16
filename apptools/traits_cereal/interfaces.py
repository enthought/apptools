#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import abstractmethod

from traits.api import ABCHasTraits, Int


class IObjectStore(ABCHasTraits):

    """ The interface required by StorageManager.store. """

    @abstractmethod
    def set(key, value):
        """ Associate `key` with `value` in the object store. """

    @abstractmethod
    def get(key):
        """ Retrieve the value associated with `key` from the object store. """


class IDeflatable(ABCHasTraits):

    """ A class which supports deflation to `apptools.traits-cereal.blob.Blob`
    """

    #: The version of the deflation algorithm used
    version = Int

    @abstractmethod
    def deflate(self, get_key):
        """ Return a `Blob` that represents the deflated object.

        Params:

        get_key(obj) : Callable
            A callable which returns the appropriate key for its argument.
        """


class IInflatable(ABCHasTraits):

    #: The version of the deflation algorithm that this inflator expects
    version = Int

    @abstractmethod
    def inflate(self, get_obj_by_key, reify=True):
        """ Inflate this intermediate object into an instance of its original
        type.

        In general, `reify` should only be False when using inflate as an
        intermediate step (possibly due to subclassing), otherwise assumptions
        about object identity when retrieving from storage may not hold.

        Params:

        get_obj_by_key(key, reify=reify) : callable
            A callable which returns the object associated with `key` from the
            data store.

        reify : bool
            If reify is True, return the fully instantiated object that the
            adaptee Blob represents.
            Otherwise, return a `Blob` with the set of children populated with
            the necessary child Blobs.

        """
