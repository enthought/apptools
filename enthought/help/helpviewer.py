
# Standard library imports
import logging
import sys, os.path
import re, string

# Local imports
from robohelp_csh import rh_showhelp


# Setup a logger for this module.
logger = logging.getLogger(__name__)


# Microsoft HtmlHelp API constants
HH_DISPLAY_TOPIC = 0x0000
HH_DISPLAY_TOC = 0x0001
HH_DISPLAY_INDEX = 0x0002
HH_DISPLAY_SEARCH = 0x0003
HH_HELP_CONTEXT = 0x000f


class HelpViewer:
    """ Encapsulates access to the RoboHelp context-sensitive help API. """
    def __init__(self, help_file, map_file=None, hwnd=None, custom_wnd=None):
        self.hwnd = hwnd
        self.help_file = help_file
        self.map_file = map_file
        if ((self.map_file is not None) and (self.map_file != "")):
            try:
                self.map_IDs = _read_map_ids(self.map_file)
            except (ValueError),msg:
                logger.error(msg)
                self.map_IDs = {}
        else: self.map_IDs = {}

    def view(self, hwnd=None, custom_wnd_name=None):
        """ Displays the default topic with table of contents pane visible."""
        self.view_toc(hwnd, custom_wnd_name)

    def view_toc(self, hwnd=0, custom_wnd_name=None):
        """ Displays the default topic with table of contents pane visible."""
        if not hwnd:
            hwnd = self.hwnd
        help_string = self._add_custom_wnd(custom_wnd_name)
        rh_showhelp(hwnd, help_string, HH_DISPLAY_TOC, 0)

    def view_index(self, hwnd=0, custom_wnd_name=None):
        """ Displays the default topic with index pane visible."""
        if not hwnd:
            hwnd = self.hwnd
        help_string = self._add_custom_wnd(custom_wnd_name)
        rh_showhelp(hwnd, help_string, HH_DISPLAY_INDEX, 0)

    def view_search(self, hwnd=0, custom_wnd_name=None):
        """ Displays the default topic with the search pane visible."""
        if not hwnd:
            hwnd = self.hwnd
        help_string = self._add_custom_wnd(custom_wnd_name)
        rh_showhelp(hwnd, help_string, HH_DISPLAY_SEARCH, 0)

    def view_id(self, id, hwnd=0, custom_wnd_name=None):
        """ Displays the topic specified by `id`."""
        #print "In Helpviewer.view_id(id=%s, hwnd=%s, custom_wnd_name=%s)" % \
        #    (id, hwnd, custom_wnd_name)
        try:
            id = self.map_IDs[id]
            # print "ID after mapping: %s" % id
        except KeyError:
            pass    # Treat as an integer ID
        if not hwnd:
            hwnd = self.hwnd
        help_string = self._add_custom_wnd(custom_wnd_name)
        rh_showhelp(hwnd, help_string, HH_HELP_CONTEXT, id)

    def view_page(self, page, hwnd=0):
        """ Supports calling a page in a help project by name, rather than ID.
            This function is can be used for WebHelp, if IDs are not used. For
            HTML Help, use `view_id()`, to avoid hard-coding topic filenames."""
        if not hwnd:
            hwnd = self.hwnd
        rh_showhelp(hwnd, self.help_file + '::' + page, HH_DISPLAY_TOPIC, 0)

    def _add_custom_wnd(self, custom_wnd_name):
            if custom_wnd_name is not None:
                help_string = self.help_file + ">" + custom_wnd_name
            else:
                help_string = self.help_file
            return help_string

def _read_map_ids(map_file):
    mapIDs = {}
    if map_file:    # Read map IDs into dictionary
        try:
            mf = open(map_file, 'r')
        except IOError:
            msg = 'Cannot open the help map file, %s' % os.path.abspath(map_file)
            raise ValueError, msg
        matchstr = re.compile(
            r"""(\#define\s+)    #1 '#define' followed by whitespace
                (\w+)\s+        #2 topic ID followed by whitespace
                (\w+)            #3 map number
            """,
            re.VERBOSE)
        for line in mf.readlines():
            matched = matchstr.match(line)
            if matched:
                # Store map number (3) keyed by topic ID (2)
                mapIDs[matched.group(2)] = string.atoi(matched.group(3))
    return mapIDs


