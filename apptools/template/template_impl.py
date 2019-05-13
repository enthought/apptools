#-------------------------------------------------------------------------------
#
#  Defines the Template class, which provides a default implementation of the
#  ITemplate interface that can be used when defining templatizable objects.
#
#  Written by: David C. Morrill
#
#  Date: 07/26/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines the Template class, which provides a default implementation of the
    ITemplate interface that can be used when defining templatizable objects.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import HasPrivateTraits, Undefined, provides

from .itemplate \
    import ITemplate

#-------------------------------------------------------------------------------
#  Metadata filter for extracting 'object' and 'datasource' items:
#-------------------------------------------------------------------------------

def instance_or_datasource ( value ):
    return value in ( 'instance', 'datasource' )

#-------------------------------------------------------------------------------
#  Metadata filter for extracting traits with no 'template' metadata:
#-------------------------------------------------------------------------------

def is_none ( value ):
    return (value is None)

#-------------------------------------------------------------------------------
#  'Template' class:
#-------------------------------------------------------------------------------

class Template ( HasPrivateTraits ):
    """ Defines the Template class, which provides a default implementation of
        the ITemplate interface that can be used when defining templatizable
        objects.
    """

    implements( ITemplate )

    #-- 'ITemplate' Interface Implementation -----------------------------------

    def names_from_template ( self ):
        """ Returns a list of **TemplateDataName** objects, one for each
            bindable data source contained within the template. Each
            **TemplateDataName** object supports unresolved bindings in
            addition to resolved bindings. Also, a **TemplateDataName** may be
            marked as *optional*, meaning the if the name remains unresolved,
            the application can take an alternative action (e.g. omit the data
            from a plot, or substitute default data, etc.).

            Returns
            -------
            A list of **TemplateDataName** objects, one for each bindable data
            source contained in the template.
        """
        data_names = []

        # Recursively propagate the request to all contained templatizable
        # objects:
        for value in self.get( template = 'instance' ).values():
            if isinstance( value, list ):
                for v in value:
                    data_names.extend( v.names_from_template() )
            elif value is not None:
                data_names.extend( value.names_from_template() )

        # Add the bindings for all of our local data source objects:
        for value in self.get( template = 'datasource' ).values():
            if isinstance( value, list ):
                for v in value:
                    data_names.append( v.name_from_data_source() )
            elif value is not None:
                data_names.append( value.name_from_data_source() )

        # Return the list of TemplateDataName objects we collected:
        return data_names

    def object_from_template ( self ):
        """ Activates the object from its template data.

            Returns
            -------
            The original object.
        """
        # Convert all our data source objects to 'live' objects:
        for value in self.get( template = 'datasource' ).values():
            if isinstance( value, list ):
                for v in value:
                    v.object_from_template()
            elif value is not None:
                value.object_from_template()

        # Recursively propagate the request to all contained templatizable
        # objects:
        for value in self.get( template = 'instance' ).values():
            if isinstance( value, list ):
                for v in value:
                    v.object_from_template()
            elif value is not None:
                value.object_from_template()

        # Reset all of our 'live' objects to undefined:
        for name in self.trait_names( template = 'derived' ):
            setattr( self, name, Undefined )

        # Return ourselves as the new, live version of the object:
        return self

    def template_from_object ( self ):
        """ Returns a *templatized* version of the object that is safe for
            serialization.

            Returns
            -------
            A new object of the same class as the original.
        """
        # Mark all traits without 'template' metadata as 'transient':
        for trait in self.traits( template = is_none ).values():
            trait.transient = True

        # Collect all of the data source and templatizable objects we contain:
        contents = self.get( template = instance_or_datasource )

        # Convert them all to new objects in template form:
        for name, value in contents.items():
            if isinstance( value, list ):
                contents[ name ] = [ v.template_from_object() for v in value ]
            else:
                contents[ name ] = value.template_from_object()

        # Add all of the simple values which can just be copied:
        contents.update( self.get( template = 'copy' ) )

        # Finally return a new instance of our class containing just the
        # templatizable values:
        return self.__class__( **contents )

    def activate_template ( self ):
        """ Converts all contained 'TDerived' objects to real objects using the
            template traits of the object. This method must be overridden in
            subclasses.

            Returns
            -------
            None
        """
        raise NotImplementedError

