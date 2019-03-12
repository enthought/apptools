#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Enthought, Inc.
# Description: <Enthought util package component>
#------------------------------------------------------------------------------
""" Implementation of hooked methods. """


def add_pre(klass, method_name, callable):
    """ Adds a pre-hook to method 'method_name' on class 'klass'. """

    _add_hook(klass, method_name, callable, pre=True)

    return

def add_post(klass, method_name, callable):
    """ Adds a post-hook to method 'method_name' on class 'klass'. """

    _add_hook(klass, method_name, callable, pre=False)

    return

def remove_pre(klass, method_name, callable):
    """ Removes a pre-hook from method 'method_name' on class 'klass'. """

    _remove_hook(klass, method_name, callable, pre=True)

    return

def remove_post(klass, method_name, callable):
    """ Removes a post-hook from method 'method_name' on class 'klass'. """

    _remove_hook(klass, method_name, callable, pre=False)

    return

###############################################################################
# Private functions.
###############################################################################

def _add_hook(klass, method_name, callable, pre):
    """ Adds a pre/post hook to method 'method_name' on class 'klass'. """

    # Get the method on the klass.
    method = getattr(klass, method_name)

    # Have we already hooked it?
    if hasattr(method, '__pre__'):
        hooked_method = method

    # Obviously not!
    else:
        def hooked_method(self, *args, **kw):
            for pre in hooked_method.__pre__:
                pre(self, *args, **kw)

            result = method(self, *args, **kw)

            for post in hooked_method.__post__:
                result = post(self, result, *args, **kw)

            return result

        # Python < 2.4 does not allow this.
        try:
            hooked_method.__name__ = method_name

        except:
            pass

        hooked_method.__pre__  = []
        hooked_method.__post__ = []

        # Is the original method actually defined on the class, or is it
        # inherited?
        hooked_method.__inherited__ = method_name not in klass.__dict__

        # Save the original method...
        #
        # fixme: Twisted uses 'method.im_func' instead of 'method' here, but
        # both seem to work just as well!
        setattr(klass, '__hooked__' + method_name, method)

        # ... and put in the hooked one!
        setattr(klass, method_name, hooked_method)

    if pre:
        hooked_method.__pre__.append(callable)

    else:
        hooked_method.__post__.append(callable)

    return

def _remove_hook(klass, method_name, callable, pre):
    """ Removes a pre/post hook from method 'method_name' on class 'klass'. """

    # Get the method on the klass.
    method = klass.__dict__[method_name]

    # Is it actually hooked?
    if hasattr(method, '__pre__'):
        # Remove the hook.
        if pre:
            method.__pre__.remove(callable)

        else:
            method.__post__.remove(callable)

        # If there are no more hooks left then cleanup.
        if len(method.__pre__) == 0 and len(method.__post__) == 0:
            # If the method is inherited then just delete the hooked version.
            if method.__inherited__:
                delattr(klass, method_name)

            # Otherwise, reinstate the original method.
            else:
                original = getattr(klass, '__hooked__' + method_name)
                setattr(klass, method_name, original)

            # Remove the saved original method.
            delattr(klass, '__hooked__' + method_name)

    return

#### EOF ######################################################################
