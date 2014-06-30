#!/usr/bin/env python
# -*- coding: utf-8 -*-

from traits.api import HasTraits


def assert_container_has_no_HasTraits(obj):
    assert not isinstance(obj, HasTraits)

    # Strings are iterable but we never want to iterate over them...
    if isinstance(obj, basestring):  # noqa
        return

    if isinstance(obj, dict):
        assert_container_has_no_HasTraits(obj.items())
        return

    try:
        for value in obj:
            assert_container_has_no_HasTraits(value)
    except TypeError:
        # This isn't a container but we already know it's not a HasTraits
        pass
