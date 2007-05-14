""" Context-sensitive help API for Adobe RoboHelp projects.

    :Copyright: 2004, Enthought, Inc.
    :License: BSD Style
    
    This file corresponds to the RoboHelp_CSH.* files provided with Adobe 
    RoboHelp X5 for C++, VB, Java, and Javascript. However, this file is a less
    robust subset of those files. It supports HMTL Help on Win32, and WebHelp 
    on other platforms. It does not support WinHelp, FlashHelp, WebHelp 
    Enterprise, or "airplane" help.
"""

import os
import atexit
from webbrowser import get, Error

from enthought.logger import logger

# Help constants
HH_DISPLAY_TOPIC = 0x0000
HH_DISPLAY_TOC = 0x0001
HH_DISPLAY_INDEX = 0x0002
HH_DISPLAY_SEARCH = 0x0003
HH_HELP_CONTEXT = 0x000f

# Get the browser controller on load
browser = None
try:
    browser = get()
    logger.debug("Found browser controller: %s" % browser)
except (Error), msg:
    logger.error(msg)


def rh_showhelp( hparent, help_file, command, data):
    """ Displays a help project. 
    
        For HTML Help on Win32, it uses the HTML Help Viewer. Otherwise, it 
        assumes WebHelp format and uses the default platform browser.
    
        Parameters
        ----------
        hparent : integer
            Handle to the parent window. This is reserved for future versions 
            of the API. Can be a window handle or 0.
        help_file : string
            For standard WebHelp, this is the path to the help project start 
            page, which can be local or on a web server: 
            "http://www.myurl.com/help/help.htm" or "/help/help.htm".
            For custom windows (defined in the help project), add ">" followed 
            by the window name: "/help/help.htm>mywin".
        command
            Command for what to display. One of the following:
                - HH_HELP_CONTEXT : Displays the topic associated with the map 
                  number sent in `data`.
                - HH_DISPLAY_SEARCH : Displays the search pane and default 
                  topic.
                - HH_DISPLAY_INDEX : Displays the index pane and default topic.
                - HH_DISPLAY_TOC : Displays the table of contents pane and 
                  default topic.
        data : integer
            Map number associated with the topic to open (if using 
            HH_HELP_CONTEXT).
            
    """
    if is_html_help(help_file):
        show_html_help_csh(hparent, help_file, command, data)
    else:
        show_web_help_csh(hparent, help_file, command, data)
        
def show_html_help_csh(hparent, help_file, command, data):
    import sys
    if sys.platform=='win32':
        from ctypes import windll
    else:
        return
    libc = windll.LoadLibrary("HHCTRL.OCX")
    if help_file:
        libc.HtmlHelpA(hparent, help_file, command, data)
    
        
def show_web_help_csh(hparent, help_file, command, data):
    """ Displays WebHelp.
    """
    help_path = help_file
    
    pos = help_file.find('>')
    if pos != -1:
        help_path = help_file[:pos]
        window = help_file[pos+1:]
    else:
        window = ""
    
    if help_path:
        if command == HH_DISPLAY_TOPIC:
            help_path = help_path + '#<id=0'
        elif command == HH_HELP_CONTEXT:
            help_path = help_path + '#<id=' + str(data)
        elif command == HH_DISPLAY_INDEX:
            help_path = help_path + '#<cmd=idx'
        elif command == HH_DISPLAY_SEARCH:
            help_path = help_path + '#<cmd=fts'
        elif command == HH_DISPLAY_TOC:
            pass # don't need to append '#<cmd=toc' to get the TOC;
                 # it causes an extra window in Mozilla.
        if len(help_path) > 0:
            if window and len(window) > 0:
                help_path = help_path + '>>wnd=' + window
                
            # NOTE: With Windows and Linux Mozilla, you get a spare browser 
            # window lying around, for any command other than 'toc'.
            # The generated Javascript for WebHelp attempts to close this 
            # window, which IE allows but Mozilla does not.
            if browser is not None:
                try:
                    browser.open(path2js(help_path))
                except (OSError, Error), msg:
                    logger.error(msg)
    return

def path2js(path):
    # Escape Windows path separators
    import re
    path = re.sub(r'\\', r'\\\\', path)

    import tempfile
    js = tempfile.mktemp(suffix='.htm')
    f = open(js,'w')
    f.write('''
<html>
<script language="Javascript">
<!--
document.location.href="file:///%s";
//-->
</script>
</html>
''' % (path))
    f.close()
    def rm_file(name=js):
        try: os.remove(name)
        except OSError: pass
    atexit.register(rm_file)
    return js

def is_html_help(help_source):
    # logger.debug("Help file is " + help_source)
    if help_source.find('.chm') != -1:
        return True
    else:
        return False
        
def is_web_help(help_source):
    if help_source.find('.htm') != -1:
        return True
    else:
        return False
        
