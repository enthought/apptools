""" Useful functions to do with types!

fixme: I don't really like collections of functions, but I'm not sure where
these should go? Class methods on 'TypeManager'?

"""


# Standard library imports.
from inspect import getclasstree


def sort_by_class_tree(objs):
    """ Sorts a list of objects by their class tree.

    Each item in the list should inherit from a common base class.

    The list is returned ordered from the most specific to the least specific.

    """

    # Since all objects must inherit from a common base class the list
    # returned by 'getclasstree' will be of length two:-
    #
    # The first element is a tuple of the form:-
    #
    # (CommonBaseClass, (HasTraits,))
    #
    # The second element is a possibly nested list containing all of the
    # classes derived from 'CommonBaseClass'.
    hierarchy = getclasstree([type(obj) for obj in objs])

    # Do an in-order traversal of the tree and return just the classes.
    #
    # This returns them ordered from least specific to most specific.
    classes = get_classes(hierarchy)

    # Note the reverse comparison (i.e., compare y with x). This is
    # because we want to return the classes ordered from the MOST
    # specfic to the least specific.
    objs.sort(key=lambda x: classes.index(type(x)), reverse=True)

    return


def get_classes(hierarchy):
    """ Walks a class hierarchy and returns all of the classes. """

    classes = []
    for item in hierarchy:
        if type(item) is tuple:
            classes.append(item[0])

        else:
            classes.extend(get_classes(item))

    return classes

#### EOF ######################################################################
