# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" An object that can be initialized from a preferences node. """


# Standard library imports.
from ast import literal_eval
import logging

# Enthought library imports.
from traits.api import HasTraits, Instance, Str, observe

# Local imports.
from .i_preferences import IPreferences
from .package_globals import get_default_preferences


# Logging.
logger = logging.getLogger(__name__)


class PreferencesHelper(HasTraits):
    """ A base class for objects that can be initialized from a preferences
    node.

    Additional traits defined on subclasses will be listened to. Changes
    are then synchronized with the preferences. Note that mutations on nested
    containers e.g. List(List(Str)) cannot be synchronized and should be
    avoided.
    """

    #### 'PreferencesHelper' interface ########################################

    # The preferences node used by the helper. If this trait is not set then
    # the package-global default preferences node is used.
    #
    # fixme: This introduces a 'sneaky' global reference to the preferences
    # node!
    preferences = Instance(IPreferences)

    # The path to the preference node that contains the preferences that we
    # use to initialize instances of this class.
    preferences_path = Str

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **traits):
        """ Constructor. """

        super(PreferencesHelper, self).__init__(**traits)

        # Initialize the object's traits from the preferences node.
        if self.preferences:
            self._initialize(self.preferences)

    ###########################################################################
    # Private interface.
    ###########################################################################

    #### Trait initializers ###################################################

    def _preferences_default(self):
        """ Trait initializer. """

        # If no specific preferences node is set then we use the package-wide
        # global node.
        return get_default_preferences()

    #### Trait change handlers ################################################

    def _anytrait_changed(self, trait_name, old, new):
        """ Static trait change handler. """

        if self.preferences is None:
            return

        if self._is_preference_trait(trait_name):
            self.preferences.set("%s.%s" % (self._get_path(), trait_name), new)

        # If the trait was a list or dict '_items' trait then just treat it as
        # if the entire list or dict was changed.
        elif trait_name.endswith('_items'):
            trait_name = trait_name[:-6]
            if self._is_preference_trait(trait_name):
                self.preferences.set(
                    '%s.%s' % (self._get_path(), trait_name),
                    getattr(self, trait_name)
                )

        # If the change refers to a trait defined on this class, then
        # the trait is not a preference trait and we do nothing.

    @observe("preferences", post_init=True)
    def _update_preferences_listeners(self, event):
        """Update listeners when the preferences object changes."""

        old, new = event.old, event.new

        # Stop listening to the old preferences node.
        if old is not None:
            old.remove_preferences_listener(
                self._preferences_changed_listener, self._get_path()
            )

        if new is not None:
            # Initialize with the new preferences node (this also adds a
            # listener for preferences being changed in the new node).
            self._initialize(new, notify=True)

    #### Other observer pattern listeners #####################################

    def _preferences_changed_listener(self, node, key, old, new):
        """ Listener called when a preference value is changed. """

        if key in self.trait_names():
            setattr(self, key, self._get_value(key, new))

    #### Methods ##############################################################

    def _get_path(self):
        """ Return the path to our preferences node. """

        if len(self.preferences_path) > 0:
            path = self.preferences_path

        else:
            path = getattr(self, "PREFERENCES_PATH", None)
            if path is None:
                raise SystemError("no preferences path, %s" % self)

            else:
                logger.warn('DEPRECATED: use "preferences_path" %s' % self)

        return path

    def _get_value(self, trait_name, value):
        """Get the actual value to set.

        This method makes sure that any required work is done to convert the
        preference value from a string. Str traits or those with the metadata
        'is_str=True' will just be passed the string itself.

        """

        trait = self.trait(trait_name)
        handler = trait.handler

        # If the trait type is 'Str' then we just take the raw value.
        if isinstance(handler, Str) or trait.is_str:
            pass

        # Otherwise, we literal_eval it!  This is safe against arbitrary code
        # execution, but it does limit values to core Python data types.
        else:
            try:
                value = literal_eval(value)

            # If the eval fails then there is probably a syntax error, but
            # we will let the handler validation throw the exception.
            except Exception:
                pass

        if handler.validate is not None:
            # Any traits have a validator of None.
            validated = handler.validate(self, trait_name, value)
        else:
            validated = value

        return validated

    def _initialize(self, preferences, notify=False):
        """ Initialize the object's traits from the preferences node. """

        path = self._get_path()
        keys = preferences.keys(path)

        traits_to_set = {}
        for trait_name in self.trait_names():
            if trait_name in keys:
                key = "%s.%s" % (path, trait_name)
                value = self._get_value(trait_name, preferences.get(key))
                traits_to_set[trait_name] = value

        self.trait_set(trait_change_notify=notify, **traits_to_set)

        # Listen for changes to the node's preferences.
        preferences.add_preferences_listener(
            self._preferences_changed_listener, path
        )

    # fixme: Pretty much duplicated in 'PreferencesPage' (except for the
    # class name of course!).
    def _is_preference_trait(self, trait_name):
        """ Return True if a trait represents a preference value. """

        if (
            trait_name.startswith("_")
            or trait_name.endswith("_")
            or trait_name in PreferencesHelper.class_traits()
        ):
            return False

        return trait_name in self.editable_traits()
