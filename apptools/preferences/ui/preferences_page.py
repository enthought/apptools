""" A page in a preferences dialog. """


# Enthought library imports.
from apptools.preferences.api import PreferencesHelper
from traits.api import Any, Dict, Str, provides

# Local imports.
from .i_preferences_page import IPreferencesPage


@provides(IPreferencesPage)
class PreferencesPage(PreferencesHelper):
    """ A page in a preferences dialog. """



    #### 'IPreferencesPage' interface #########################################

    # The page's category (e.g. 'General/Appearance'). The empty string means
    # that this is a top-level page.
    category = Str

    # DEPRECATED: The help_id was never fully implemented, and it's been
    # over two years (now 4/2009).  The original goal was for the the Help
    # button to automatically appear and connect to a help page with a
    # help_id.  Not removing the trait right now to avoid breaking code
    # that may be checking for this.
    #
    # Use PreferencesManager.show_help and trait show_help metadata instead.
    help_id = Str

    # The page name (this is what is shown in the preferences dialog.
    name = Str

    #### Private interface ####################################################

    # The traits UI that represents the page.
    _ui = Any

    # A dictionary containing the traits that have been changed since the
    # last call to 'apply'.
    _changed = Dict

    ###########################################################################
    # 'IPreferencesPage' interface.
    ###########################################################################

    def apply(self):
        """ Apply the page's preferences. """

        path = self._get_path()

        for trait_name, value in self._changed.items():
            if self._is_preference_trait(trait_name):
                self.preferences.set('%s.%s' % (path, trait_name), value)

        self._changed.clear()

        return

    # fixme: We would like to be able to have the following API so that
    # developers are not forced into using traits UI for their preferences
    # pages, but at the moment I can't work out how to do it!
##     def create_control(self, parent):
##         """ Create the toolkit-specific control that represents the page. """

##         if self._ui is None:
##             self._ui = self.edit_traits(parent=parent, kind='subpanel')

##         return self._ui.control

##     def destroy_control(self):
##         """ Destroy the toolkit-specific control that represents the page. """

##         if self._ui is not None:
##             self._ui.dispose()
##             self._ui = None

##         return

    ###########################################################################
    # Private interface.
    ###########################################################################

    #### Trait change handlers ################################################

    def _anytrait_changed(self, trait_name, old, new):
        """ Static trait change handler.

        This is an important override! In the base-class when a trait is
        changed the preferences node is updated too. Here, we stop that from
        happening and just make a note of what changes have been made. The
        preferences node gets updated when the 'apply' method is called.

        """

        # If the trait was a list or dict '_items' trait then just treat it as
        # if the entire list or dict was changed.
        if trait_name.endswith('_items'):
            trait_name = trait_name[:-6]
            if self._is_preference_trait(trait_name):
                self._changed[trait_name] = getattr(self, trait_name)

        elif self._is_preference_trait(trait_name):
            self._changed[trait_name] = new

        return

    # fixme: Pretty much duplicated in 'PreferencesHelper' (except for the
    # class name of course!).
    def _is_preference_trait(self, trait_name):
        """ Return True if a trait represents a preference value. """

        if trait_name.startswith('_') or trait_name.endswith('_') \
           or trait_name in PreferencesPage.class_traits():
            return False

        return True

#### EOF ######################################################################
