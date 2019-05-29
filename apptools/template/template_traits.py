#-------------------------------------------------------------------------------
#
#  Trait definitions useful when creating templatizable classes.
#
#  Written by: David C. Morrill
#
#  Date: 07/26/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Trait definitions useful when creating templatizable classes.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import Instance, Int, Float, Str, List, Bool, Range, TraitType, Undefined

from .itemplate_data_source \
    import ITemplateDataSource

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Data source template trait:
TDataSource = Instance( ITemplateDataSource, template = 'datasource' )

# Templatizable object trait:
def TInstance ( *args, **kw ):
    kw[ 'template' ] = 'instance'
    return Instance( *args, **kw )

# A list of templatizable object traits:
def TList( *args, **kw ):
    kw[ 'template' ] = 'instance'
    return List( *args, **kw )

# Simple, copyable template traits:
TInt   = Int(   template = 'copy' )
TFloat = Float( template = 'copy' )
TStr   = Str(   template = 'copy' )
TBool  = Bool(  template = 'copy' )

def TRange ( *args, **kw ):
    kw[ 'template' ] = 'copy'
    return Range( *args, **kw )

def TEnum ( *args, **kw ):
    kw[ 'template' ] = 'copy'
    return Enum( *args, **kw )

#-------------------------------------------------------------------------------
#  'TDerived' trait:
#-------------------------------------------------------------------------------

class TDerived ( TraitType ):
    """ Defines a trait property for handling attributes whose value depends
        upon the templatizable traits of an object.

        Note that the implementation of the *activate_template* method is not
        allowed to read the value of any **TDerived** traits, it may only set
        them.
    """

    # Base trait metadata:
    metadata = { 'template':  'derived',
                 'transient': True }

    def get ( self, object, name ):
        name += '_'
        value = object.__dict__.get( name, Undefined )
        if value is not Undefined:
            return value

        object.activate_template()

        value = object.__dict__.get( name, Undefined )
        if value is not Undefined:
            return value

        object.__dict__[ name ] = None
        return None

    def set ( self, object, name, value ):
        xname = name + '_'
        old   = object.__dict__.get( xname, Undefined )
        if old is not value:
            object.__dict__[ xname ] = value
            object.trait_property_changed( name, old, value )

