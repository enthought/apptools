#!/usr/bin/env python
# -*- coding: utf-8 -*-

from storables import Parent, Child
from apptools.traits_cereal.storage_manager import StorageManager
from pprint import pformat as fmt

pformat = lambda x: fmt(x, indent=1)


def main():
    """Run main."""

    child = Child(bar=1)
    parent = Parent(child=child)

    print("Parent: \n{}".format(pformat(parent.get())))
    print("Child: \n{}".format(pformat(child.get())))

    sm = StorageManager()

    # Write our objects out to... wherever
    parent_blob_key = sm.save(parent)
    child_blob_key = sm.save(child)

    # For the example, make sure we are pulling out of dry storage and not
    # cache. One wouldn't normally need (or want!) to call this.
    sm._cache.clear()

    print("================================================")

    # Bring them back to life
    re_parent = sm.load(parent_blob_key)
    print("Parent: \n{}".format(pformat(re_parent.get())))
    re_parent_child = re_parent.child
    print("Parent.Child: \n{}".format(pformat(re_parent_child.get())))

    re_child = sm.load(child_blob_key)
    print("Child: \n{}".format(pformat(re_child.get())))

    assert re_child is re_parent_child

    return


if __name__ == '__main__':
    main()
