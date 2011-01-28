#-------------------------------------------------------------------------------
#
#  Helper functions/classes useful for implementing various template interfaces.
#
#  Written by: David C. Morrill
#
#  Date: 07/29/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Returns a properly joined path name:
#-------------------------------------------------------------------------------

def path_for ( *names ):
    """ Returns a properly joined path name (i.e. the elements of the name are
        separated by '.').
    """
    return '.'.join( [ name for name in names if name != '' ] )

#-------------------------------------------------------------------------------
#  Parses a possible compound data context name:
#-------------------------------------------------------------------------------

def parse_name ( name ):
    """ Parses a possible compound data context name.
    """
    return name.split( '.' )

