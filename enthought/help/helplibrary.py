
# Standard library imports.
import logging

# Enthought library imports
from enthought.traits.api import Dict, DictStrStr, SingletonHasPrivateTraits, Str

# Local imports
from helpviewer import HelpViewer


# Setup a logger for this module.
logger = logging.getLogger(__name__)


class HelpLibrary(SingletonHasPrivateTraits):
    """Manages a collection of help projects."""

    _library = Dict(key_trait=Str, value_trait=HelpViewer)
    _custom_windows = DictStrStr


    def add_helpproject(self, proj_id, help_file, map_file, custom_wnd=None):
        """ Creates a viewer for a help project, and adds it to the library.

            If the help project ID is already in use, its existing viewer is
            replaced by the new viewer.
        """
        self._library[proj_id] = HelpViewer(help_file, map_file)
        self._custom_windows[proj_id] = custom_wnd

    def get_helpproject(self, proj_id):
        """ Returns the viewer associated with a help project ID."""
        if self._library.has_key(proj_id):
            return self._library[proj_id]
        else:
            return None

    def show_topic(self, topic_string):
        """ Parses a topic string of the form 'proj_id|topic_id' and calls the
            viewer associated with the project ID to display the topic associated
            with the topic ID.
        """
        # print "In show_topic(), topic_string='%s'" % topic_string
        if topic_string is None:
            return
        elif '|' not in topic_string:
            logger.warn("Invalid help ID string, missing '|' in '%s'" % topic_string)
            return
        else:
            proj, topic = topic_string.split('|')
            viewer = self.get_helpproject(proj)
            logger.debug("Using HelpViewer for: %s" % viewer.help_file)
            if viewer is not None:
                custom_wnd = self._custom_windows[proj]
                viewer.view_id(topic, custom_wnd_name=custom_wnd)

    def show_toc(self, proj_id):
        """ Displays the TOC of the specified help project.
        """
        viewer = self.get_helpproject(proj_id)
        if viewer is not None:
            viewer.view_toc()


# Global help library
_helplibrary = HelpLibrary()

# Return the global help library
def helplibrary():
    return _helplibrary

def test_helplibrary():
    hl = _helplibrary
    print "HelpLibrary instance: %s" % hl
    proj_id = "Test01"
    topic_string = "Test01|Preferences_Dialog_Box"
    hl.add_helpproject(proj_id, "./TestHelp/TestHelp.chm", "./TestHelp/BSSCDefault.h")
    hv = hl.get_helpproject(proj_id)
    print "Viewer for Project %s is %s" % (proj_id, hv)
    hl.show_topic(topic_string)

if __name__ == '__main__':
    test_helplibrary()


