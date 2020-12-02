# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# Update class names from the immediately prior version only
# to ensure that cycles are not possible

from apptools.persistence.updater import Updater


def update_project(self, state):
    print('updating to v2')
    metadata = state['metadata']
    metadata['version'] = 2
    metadata['updater'] = 22
    return state


class Update2(Updater):

    def __init__(self):

        self.refactorings = {
            ("__main__", "Foo1"): ("__main__", "Foo2"),
        }

        self.setstates = {
            ("cplab.project", "Project"): update_project
        }
