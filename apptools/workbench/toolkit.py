""" Toolkit management. """

# This will determine the Pyface backend, which we will use.
from pyface.toolkit import toolkit_object as pyface_toolkit


def toolkit_object(name):
    """ Return the toolkit specific object with the given name.

    Parameters
    ----------
    name : str
        The name consists of the relative module path and the object name
        separated by a colon.
    """
    import os
    import sys
    import importlib

    package = 'apptools.workbench.' + pyface_toolkit.toolkit

    mname, oname = name.split(':')
    try:
        module = importlib.import_module('.' + mname, package)
    except ImportError as exc:
        # is the error while trying to import package mname or not?
        if all(part not in exc.args[0] for part in mname.split('.')):
            # something else went wrong - let the exception be raised
            raise

        # Ignore *ANY* errors unless a debug ENV variable is set.
        if 'ETS_DEBUG' in os.environ:
            # Attempt to only skip errors in importing the backend modules.
            # The idea here is that this only happens when the last entry in
            # the traceback's stack frame mentions the toolkit in question.
            import traceback
            frames = traceback.extract_tb(sys.exc_traceback)
            filename, lineno, function, text = frames[-1]
            if not package in filename:
                raise
    else:
        obj = getattr(module, oname, None)
        if obj is not None:
            return obj

    class Unimplemented(object):
        """ An unimplemented toolkit object

        This is returned if an object isn't implemented by the selected
        toolkit.  It raises an exception if it is ever instantiated.
        """

        def __init__(self, *args, **kwargs):
            msg = "the %s workbench backend doesn't implement %s"
            raise NotImplementedError(msg % (pyface_toolkit.toolkit, name))

    return Unimplemented
