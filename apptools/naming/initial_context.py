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
# Description: <Enthought naming package component>
#------------------------------------------------------------------------------
""" The starting point for performing naming operations. """


# Local imports.
from .context import Context


def InitialContext(environment):
    """ Creates an initial context for beginning name resolution. """

    # Get the class name of the factory that will produce the initial context.
    klass_name = environment.get(Context.INITIAL_CONTEXT_FACTORY)
    if klass_name is None:
        raise ValueError("No initial context factory specified")

    # Import the factory class.
    klass = _import_symbol(klass_name)

    # Create the factory.
    factory = klass()

    # Ask the factory for a context implementation instance.
    return factory.get_initial_context(environment)


# fixme: This is the same code as in the Envisage import manager but we don't
# want naming to be dependent on Envisage, so we need some other package
# for useful 'Python' tools etc.
def _import_symbol(symbol_path):
    """ Imports the symbol defined by 'symbol_path'.

    'symbol_path' is a string in the form 'foo.bar.baz' which is turned
    into an import statement 'from foo.bar import baz' (ie. the last
    component of the name is the symbol name, the rest is the package/
    module path to load it from).

    """

    components = symbol_path.split('.')

    module_name = '.'.join(components[:-1])
    symbol_name = components[-1]

    module = __import__(module_name, globals(), locals(), [symbol_name])
    symbol = getattr(module, symbol_name)

    return symbol

#### EOF ######################################################################
