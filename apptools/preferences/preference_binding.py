""" A binding between a trait on an object and a preference value. """


# Enthought library imports.
from traits.api import Any, HasTraits, Instance, Str, Undefined
from traits.api import Unicode

# Third-party librart imports.
import six

# Local imports.
from .i_preferences import IPreferences
from .package_globals import get_default_preferences


class PreferenceBinding(HasTraits):
    """ A binding between a trait on an object and a preference value. """

    #### 'PreferenceBinding' interface ########################################

    # The object that we are binding the preference to.
    obj = Any

    # The preferences node used by the binding. If this trait is not set then
    # the package-global default preferences node is used (and if that is not
    # set then the binding won't work ;^)
    preferences = Instance(IPreferences)

    # The path to the preference value.
    preference_path = Str

    # The name of the trait that we are binding the preference to.
    trait_name = Str

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **traits):
        """ Constructor. """

        super(PreferenceBinding, self).__init__(**traits)

        # Initialize the object's trait from the preference value.
        self._set_trait(notify=False)

        # Wire-up trait change handlers etc.
        self._initialize()

        return

    ###########################################################################
    # 'PreferenceBinding' interface.
    ###########################################################################

    #### Trait initializers ###################################################

    def _preferences_default(self):
        """ Trait initializer. """

        return get_default_preferences()

    ###########################################################################
    # Private interface.
    ###########################################################################

    #### Trait change handlers ################################################

    def _on_trait_changed(self, obj, trait_name, old, new):
        """ Dynamic trait change handler. """

        self.preferences.set(self.preference_path, new)

        return

    #### Other observer pattern listeners #####################################

    def _preferences_listener(self, node, key, old, new):
        """ Listener called when a preference value is changed. """

        components = self.preference_path.split('.')
        if key == components[-1]:
            self._set_trait()

        return

    #### Methods ##############################################################

    # fixme: This method is mostly duplicated in 'PreferencesHelper' (the only
    # difference is the line that gets the handler).
    def _get_value(self, trait_name, value):
        """ Get the actual value to set.

        This method makes sure that any required work is done to convert the
        preference value from a string.

        """

        handler = self.obj.trait(trait_name).handler

        # If the trait type is 'Str' then we just take the raw value.
        if type(handler) is Str:
            pass

        # If the trait type is 'Unicode' then we convert the raw value.
        elif type(handler) is Unicode:
            value = six.text_type(value)

        # Otherwise, we eval it!
        else:
            try:
                value = eval(value)

            # If the eval fails then there is probably a syntax error, but
            # we will let the handler validation throw the exception.
            except:
                pass

        return handler.validate(self, trait_name, value)

    def _initialize(self):
        """ Wire-up trait change handlers etc. """

        # Listen for the object's trait being changed.
        self.obj.on_trait_change(self._on_trait_changed, self.trait_name)

        # Listen for the preference value being changed.
        components = self.preference_path.split('.')
        node       = '.'.join(components[:-1])

        self.preferences.add_preferences_listener(
            self._preferences_listener, node
        )

        return

    def _set_trait(self, notify=True):
        """ Set the object's trait to the value of the preference. """

        value = self.preferences.get(self.preference_path, Undefined)
        if value is not Undefined:
            trait_value = self._get_value(self.trait_name, value)
            traits      = {self.trait_name : trait_value}

            self.obj.trait_set(trait_change_notify=notify, **traits)

        return


# Factory function for creating bindings.
def bind_preference(obj, trait_name, preference_path, preferences=None):
    """ Create a new preference binding. """

    # This may seem a bit wierd, but we manually build up a dictionary of
    # the traits that need to be set at the time the 'PreferenceBinding'
    # instance is created.
    #
    # This is because we only want to set the 'preferences' trait iff one
    # is explicitly specified. If we passed it in with the default argument
    # value of 'None' then it counts as 'setting' the trait which prevents
    # the binding instance from defaulting to the package-global preferences.
    # Also, if we try to set the 'preferences' trait *after* construction time
    # then it is too late as the binding initialization is done in the
    # constructor (we could of course split that out, which may be the 'right'
    # way to do it ;^).
    traits = {
        'obj'             : obj,
        'trait_name'      : trait_name,
        'preference_path' : preference_path
    }

    if preferences is not None:
        traits['preferences'] = preferences

    return PreferenceBinding(**traits)

#### EOF ######################################################################
