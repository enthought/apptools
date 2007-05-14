""" Displays the TOC for the Sample Help Project. """


# Enthought library imports.
from enthought.envisage import get_application

from enthought.pyface.action.api import Action
from enthought.traits.api import HasTraits, Str
from enthought.traits.ui.api import View, Group

from enthought.help.help_plugin import IHELP

from sample_help_project_plugin_definition import sample_help_project

proj_id = sample_help_project.proj_id


class SampleHelpProjectAction(Action):
    """ Displays the help dialog. """
    ###########################################################################
    # 'Action' interface.
    ###########################################################################

    def perform(self):
        """ Performs the action. """                

        plugin = get_application().get_service(IHELP)
        plugin.library.show_toc(proj_id)

        return

class SampleTraitsHelpAction(Action):
    
    def perform(self):
        Person().edit_traits()
        

class Person(HasTraits):
    first_name = Str
    last_name = Str
    trait_view = View(
                    Group('first_name', 'last_name'),
                    help = True,
                    help_id = proj_id + "|Preferences_Dialog_Box",
                    )
#### EOF ######################################################################
