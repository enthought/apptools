# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


def __replacement_setstate__(self, state):
    """"""
    state = self.__updater__(state)
    self.__dict__.update(state)


class Updater:

    """An abstract class to provide functionality common to the updaters."""

    def get_latest(self, module, name):
        """The refactorings dictionary contains mappings between old and new
        module names.  Since we only bump the version number one increment
        there is only one possible answer.
        """
        if hasattr(self, "refactorings"):
            module = self.strip(module)
            name = self.strip(name)
            # returns the new module and name if it exists otherwise defaults
            # to using the original module and name
            module, name = self.refactorings.get(
                (module, name), (module, name)
            )

        return module, name

    def strip(self, string):
        # Who would have thought that pickle would pass us
        # names with \013 on the end? Is this after the files have
        # manually edited?
        if ord(string[-1:]) == 13:
            return string[:-1]

        return string
