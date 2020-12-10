.. _preferences-in-envisage:

Preferences in Envisage
=======================

This section discusses how an Envisage application uses the preferences
mechanism. Envisage tries not to dictate too much, and so this describes the
default behaviour, but you are free to override it as desired.

Envisage uses the default implementation of the |ScopedPreferences| class which
is made available via the application's 'preferences' trait::

  >>> application = Application(id='myapplication')
  >>> application.preferences.set('acme.ui.bgcolor', 'yellow')
  >>> application.preferences.get('acme.ui.bgcolor')
  'yellow'

Hence, you use the Envisage preferences just like you would any other scoped
preferences.

It also registers itself as the default preferences node used by the
|PreferencesHelper| class. Hence you don't need to provide a preferences node
explicitly to your helper::

  >>> helper = SplashScreenPreferences()
  >>> helper.bgcolor
  'blue'
  >>> helper.width
  100
  >>> helper.ratio
  1.0
  >>> helper.visible
  True

The only extra thing that Envisage does for you is to provide an extension
point that allows you to contribute any number of '.ini' files that are
loaded into the default scope when the application is started.

e.g. To contribute a preference file for my plugin I might use::

  class MyPlugin(Plugin):
      ...

      @contributes_to('envisage.preferences')
      def get_preferences(self, application):
          return ['pkgfile://mypackage:preferences.ini']

..
   # substitutions

.. |PreferencesHelper| replace:: :class:`~apptools.preferences.preferences_helper.PreferencesHelper`
.. |ScopedPreferences| replace:: :class:`~apptools.preferences.scoped_preferences.ScopedPreferences`
