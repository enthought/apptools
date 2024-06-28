# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" A Python based configuration file with hierarchical sections. """


class PyConfigFile(dict):
    """ A Python based configuration file with hierarchical sections. """

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, file_or_filename=None):
        """Constructor.

        If 'file_or_filename' is specified it will be loaded immediately. It
        can be either:-

        a) a filename
        b) a file-like object that must be open for reading

        """

        # A dictionary containing one namespace instance for each root of the
        # config hierarchy (see the '_Namespace' class for more details).
        #
        # e.g. If the following sections have been loaded:-
        #
        # [acme.foo]
        # ...
        # [acme.bar]
        # ...
        # [tds]
        # ...
        # [tds.baz]
        # ...
        #
        # Then the dictionary will contain:-
        #
        # {'acme' : <A _Namespace instance>, 'tds' : <A _Namespace instance>}
        #
        self._namespaces = {}

        if file_or_filename is not None:
            self.load(file_or_filename)

    ###########################################################################
    # 'PyConfigFile' interface.
    ###########################################################################

    def load(self, file_or_filename):
        """Load the configuration from a file.

        'file_or_filename' can be either:-

        a) a filename
        b) a file-like object that must be open for reading

        """

        # Get an open file to read from.
        f = self._get_file(file_or_filename)

        section_name = None
        section_body = ""
        for line in f:
            stripped = line.strip()

            # Is this line a section header?
            #
            # If so then parse the preceding section (if there is one) and
            # start collecting the body of the new section.
            if stripped.startswith("[") and stripped.endswith("]"):
                if section_name is not None:
                    self._parse_section(section_name, section_body)

                section_name = stripped[1:-1]
                section_body = ""

            # Otherwise, this is *not* a section header so add the line to the
            # body of the current section. If there is no current section then
            # we simply ignore it!
            else:
                if section_name is not None:
                    section_body += line

        # Parse the last section in the file.
        if section_name is not None:
            self._parse_section(section_name, section_body)

        f.close()

    def save(self, file_or_filename):
        """Save the configuration to a file.

        'file_or_filename' can be either:-

        a) a filename
        b) a file-like object that must be open for writing

        """

        f = self._get_file(file_or_filename, "w")

        for section_name, section_data in self.items():
            self._write_section(f, section_name, section_data)

        f.close()

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _get_file(self, file_or_filename, mode="r"):
        """Return an open file object from a file or a filename.

        The mode is only used if a filename is specified.

        """

        if isinstance(file_or_filename, str):
            f = open(file_or_filename, mode)

        else:
            f = file_or_filename

        return f

    def _get_namespace(self, section_name):
        """ Return the namespace that represents the section. """

        components = section_name.split(".")
        namespace = self._namespaces.setdefault(components[0], _Namespace())

        for component in components[1:]:
            namespace = getattr(namespace, component)

        return namespace

    def _parse_section(self, section_name, section_body):
        """Parse a section.

        In this implementation, we don't actually 'parse' anything - we just
        execute the body of the section as Python code ;^)

        """

        # If this is the first time that we have come across the section then
        # start with an empty dictionary for its contents. Otherwise, we will
        # update its existing contents.
        section = self.setdefault(section_name, {})

        # Execute the Python code in the section dictionary.
        #
        # We use 'self._namespaces' as the globals for the code execution so
        # that config values can refer to other config values using familiar
        # Python syntax (see the '_Namespace' class for more details).
        #
        # e.g.
        #
        # [acme.foo]
        # bar = 1
        # baz = 99
        #
        # [acme.blargle]
        # blitzel = acme.foo.bar + acme.foo.baz
        exec(section_body, self._namespaces, section)

        # The '__builtins__' dictionary gets added to 'self._namespaces' as
        # by the call to 'exec'. However, we want 'self._namespaces' to only
        # contain '_Namespace' instances, so we do the cleanup here.
        del self._namespaces["__builtins__"]

        # Get the section's corresponding node in the 'dotted' namespace and
        # update it with the config values.
        namespace = self._get_namespace(section_name)
        namespace.__dict__.update(section)

    def _write_section(self, f, section_name, section_data):
        """ Write a section to a file. """

        f.write("[%s]\n" % section_name)

        for name, value in section_data.items():
            f.write("%s = %s\n" % (name, repr(value)))

        f.write("\n")

    ###########################################################################
    # Debugging interface.
    ###########################################################################

    def _pretty_print_namespaces(self):
        """ Pretty print the 'dotted' namespaces. """

        for name, value in self._namespaces.items():
            print("Namespace:", name)
            value.pretty_print("  ")


###############################################################################
# Internal use only.
###############################################################################


class _Namespace(object):
    """An object that represents a node in a dotted namespace.

    We build up a dotted namespace so that config values can refer to other
    config values using familiar Python syntax.

    e.g.

    [acme.foo]
    bar = 1
    baz = 99

    [acme.blargle]
    blitzel = acme.foo.bar + acme.foo.baz

    """

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __getattr__(self, name):
        """ Return the attribute with the specified name. """

        # This looks a little weird, but we are simply creating the next level
        # in the namespace hierarchy 'on-demand'.
        namespace = self.__dict__[name] = _Namespace()

        return namespace

    ###########################################################################
    # Debugging interface.
    ###########################################################################

    def pretty_print(self, indent=""):
        """ Pretty print the namespace. """

        for name, value in self.__dict__.items():
            if isinstance(value, _Namespace):
                print(indent, "Namespace:", name)
                value.pretty_print(indent + "  ")

            else:
                print(indent, name, ":", value)
