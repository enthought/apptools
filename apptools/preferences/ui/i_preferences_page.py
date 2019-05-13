""" The interface for pages in a preferences dialog. """


# Enthought library imports.
from traits.api import Interface, Str


class IPreferencesPage(Interface):
    """ The interface for pages in a preferences dialog. """

    # The page's category (e.g. 'General/Appearence'). The empty string means
    # that this is a top-level page.
    category = Str

    # The page's help identifier (optional). If a help Id *is* provided then
    # there will be a 'Help' button shown on the preference page.
    help_id = Str

    # The page name (this is what is shown in the preferences dialog).
    name = Str

    def apply(self):
        """ Apply the page's preferences. """

    # fixme: We would like to be able to have the following API so that
    # developers are not forced into using traits UI for their preferences
    # pages, but at the moment I can't work out how to do it!
##     def create_control(self, parent):
##         """ Create the toolkit-specific control that represents the page. """

##     def destroy_control(self, parent):
##         """ Destroy the toolkit-specific control that represents the page. """

#### EOF ######################################################################
