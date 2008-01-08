""" A page in a preferences dialog. """


# Enthought library imports.
from enthought.preferences.api import PreferencesHelper
from enthought.traits.api import Any, Dict, Str, implements

# Local imports.
from i_preferences_page import IPreferencesPage


class PreferencesPage(PreferencesHelper):
    """ A page in a preferences dialog. """

    implements(IPreferencesPage)
     
    #### 'IPreferencesPage' interface #########################################
    
    # The page's category (e.g. 'General/Appearence'). The empty string means
    # that this is a top-level page.
    category = Str

    # The page's help identifier (optional). If a help Id *is* provided then
    # there will be a 'Help' button shown on the preference page.
    #
    # fixme: The 'Help' button is not implemented yet - but you can still
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
        
    def create_control(self, parent):
        """ Create the toolkit-specific control that represents the page. """
    
        if self._ui is None:
            self._ui = self.edit_traits(parent=parent, kind='subpanel')

        return self._ui.control

    def destroy_control(self):
        """ Destroy the toolkit-specific control that represents the page. """

        if self._ui is not None:
            self._ui.dispose()
            self._ui = None
            
        return

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

        if self._is_preference_trait(trait_name):
            self._changed[trait_name] = new

        return
    
#### EOF ######################################################################
