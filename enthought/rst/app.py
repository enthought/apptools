#------------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
#  All rights reserved.
# 
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#  
#  Author: Evan Patterson
#  Date:   06/19/2009
#
#------------------------------------------------------------------------------

# Local imports
from rest_editor_view import ReSTHTMLEditorView


def main():
    app = ReSTHTMLEditorView()
    app.configure_traits()


if __name__ == '__main__':
    main()
