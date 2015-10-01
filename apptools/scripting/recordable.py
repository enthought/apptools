"""
Decorator to mark functions and methods as recordable.
"""
# Author: Prabhu Ramachandran <prabhu@aero.iitb.ac.in>
# Copyright (c) 2008, Prabhu Ramachandran and Enthought, Inc.
# License: BSD Style.

from .package_globals import get_recorder


# Guard to ensure that only the outermost recordable call is recorded
# and nested calls ignored.
_outermost_call = True


def recordable(func):
    """A decorator that wraps a function into one that is recordable.

    This will record the function only if the global recorder has been
    set via a `set_recorder` function call.

    This is almost entirely copied from the
    apptools.appscripting.scriptable.scriptable decorator.
    """

    def _wrapper(*args, **kw):
        """A wrapper returned to replace the decorated function."""
        global _outermost_call

        # Boolean to specify if the method was recorded or not.
        record = False
        if _outermost_call:
            # Get the recorder.
            rec = get_recorder()
            if rec is not None:
                _outermost_call = False
                # Record the method if recorder is available.
                record = True
                try:
                    result = rec.record_function(func, args, kw)
                finally:
                    _outermost_call = True
        if not record:
            # If the method was not recorded, just call it.
            result = func(*args, **kw)

        return result

    # Mimic the actual function.
    _wrapper.__name__ = func.__name__
    _wrapper.__doc__ = func.__doc__
    _wrapper.__dict__.update(func.__dict__)

    return _wrapper
