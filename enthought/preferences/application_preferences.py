""" Application preferences. """


import os

from enthought.etsconfig.api import ETSConfig
from enthought.preferences.api import Preferences, ScopedPreferences
from enthought.traits.api import Str


class ApplicationPreferences(ScopedPreferences):
    """ Application preferences.

    When building applications, it is quite common to have preferences (aka
    settings etc) come from 3 different places:-

    1) The command line
    2) The user (via the preferences dialog etc)
    3) The developer (aka system defaults!)

    In such a scenario we want the command-line to take precedence over the
    user settings, and the user settings to take precedence over the system
    defaults.

    This class provides exactly this via 3 preferences scopes:-

    'command-line'
    - this scope is for any preferences specified on the command-line
    - it is a transient scope as we get the preferences each time the
      application is started.

    'user'
    - this scope is for any preferences explicitly set by the user
    - the users usually sets preference via the preferences dialog
    - this is a persistent scope which by default is saved in::
          os.path.join(ETSConfig.application_home, 'user.ini')
    - if you want to save it somewhere else, set 'user_preferences_filename'

    'default'
    - the scope is for any system defaults (usually chosen at deployment time)
    - this scope is transient but is usually loaded from .ini file(s) provided
      with the application.

    In general, if you are just getting preferences you don't need to care
    about the underlying scopes at all, you just use a call such as::

        preferences.get('acme.example.bgolor')

    And the preferences system handles looking through the scopes in the
    appropriate order.

    The only time you generally care about the scopes is if you are responsible
    for setting/loading preferences, and then you simply access the scope
    explcitly when making calls via the API.

    e.g. To set a preference in the user scope use::

        user_scope = preferences.get_scope('user')
        user_scope.set('acme.example.bgcolor', 'blue')

    For convenience you can also prefix the preference path with the scope
    name, which reduces the 2 lines above into::

        preferences.set('user/acme.example.bgcolor', 'blue')

    By default, setting a preference sets it in the user scope, so when
    loading command-line and default preferences make sure to specify the
    scope explicitly, e.g::

        preferences.set('command-line/acme.example.bgcolor', 'blue')
        preferences.set('default/acme.example.bgcolor', 'blue')
    
    """
    
    #### 'ScopedPreferences' protocol #########################################

    # This makes the user scope the default scope for 'set' operations etc.
    primary_scope_name = 'user'
    
    def _scopes_default(self):
        """ Trait initializer. """

        scopes = [
            Preferences(name='command-line'),
            Preferences(name='user', filename=self.user_preferences_filename),
            Preferences(name='default')
        ]

        return scopes

    #### 'ApplicationPreferences' protocol ####################################

    # The file that the user scope preferences are stored in.
    #
    # Defaults to:-
    #
    #    os.path.join(ETSConfig.application_home, 'user.ini')
    user_preferences_filename = Str

    def _user_preferences_filename_default(self):
        """ Trait initializer. """

        return os.path.join(ETSConfig.application_home, 'user.ini')

#### EOF ######################################################################
