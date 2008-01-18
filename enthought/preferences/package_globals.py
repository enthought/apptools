""" Package-scope globals. """


# The default preferences node.
_default_preferences = None

def get_default_preferences():
    """ Get the default preferences node. """

    return _default_preferences

def set_default_preferences(default_preferences):
    """ Set the default preferences node. """

    global _default_preferences

    _default_preferences = default_preferences

    # For convenience.
    return _default_preferences

#### EOF ######################################################################
