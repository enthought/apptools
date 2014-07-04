#!/usr/bin/env python
# -*- coding: utf-8 -*-

from traits.api import Interface


class IObjectStore(Interface):

    """ The interface required by StorageManager.store. It represents a dumb
    key-value store that knows its keys."""

    def set(key, val):
        pass

    def get(key):
        pass

    def __iter__(self):
        pass


class IDeflatable(Interface):
    def deflate(self):
        """ Prepare the object for reification.

        Typically this involves loading and populating datastructures.

        We don't return the object directly here so that these can be
        subclassed.
        """


class IInflatable(Interface):
    def inflate(self):
        """ Return a Blob representing the object. """
