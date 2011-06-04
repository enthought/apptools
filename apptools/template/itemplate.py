#-------------------------------------------------------------------------------
#
#  Defines the ITemplate interface used to create templatizable object
#  hierarchies.
#
#  Written by: David C. Morrill
#
#  Date: 07/26/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines the ITemplate interface used to create templatizable object
    hierarchies.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import Interface

#-------------------------------------------------------------------------------
#  'ITemplate' interface:
#-------------------------------------------------------------------------------

class ITemplate ( Interface ):
    """ Defines the ITemplate interface used to create templatizable object
        hierarchies.
    """

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

    def object_from_template ( self ):
        """ Activates the object from its template data.

            Returns
            -------
            The original object.
        """

    def template_from_object ( self ):
        """ Returns a *templatized* version of the object that is safe for
            serialization.

            Returns
            -------
            A new object of the same class as the original.
        """

    def activate_template ( self ):
        """ Converts all contained 'TDerived' objects to real objects using the
            template traits of the object.

            Returns
            -------
            None
        """

