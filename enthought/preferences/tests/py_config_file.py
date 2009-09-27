""" A simple(istic?) Python-esque configuration file. """


class PyConfigFile(dict):
    """ A simple(istic?) Python-esque configuration file. """

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, file_or_filename=None):
        """ Constructor. """

        # A dictionary containing a namespace object for the root of each
        # config hierarchy.
        #
        #. e.g. If the config file is:-
        #
        # [acme.foo]
        # ...
        # [acme.bar]
        # ...
        # [tds.baz]
        # ...
        #
        # Then the dictionary will contain:-
        #
        # {'acme' : <A Namespace>, 'tds' : <A Namespace>}
        #
        self._namespaces = {}

        if file_or_filename is not None:
            self.load(file_or_filename)
        
        return

    ###########################################################################
    # 'PyConfigFile' interface.
    ###########################################################################
    
    def load(self, file_or_filename):
        """ Load the configuration from a file.

        'file_or_filename' can be either:-

        a) a filename
        b) a file-like object open for reading

        """

        # Get an open file to read from.
        f = self._get_file(file_or_filename)

        section_name = None
        for line in f:
            stripped = line.strip()

            # Is this line a section header?
            #
            # If so then parse the preceding section (if there is one) and
            # start collecting the body of the new section.
            if stripped.startswith('[') and stripped.endswith(']'):
                if section_name is not None:
                    self._parse_section(section_name, section_body)

                section_name = stripped[1:-1]
                section_body = ''

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
        
        return

    def save(self, file_or_filename):
        """ Save the configuration to a file.

        'file_or_filename' can be a filename or a file-like object in write
        mode.

        """

        f = self._get_file(file_or_filename, 'w')

        for section_name, section_data in self.items():
            self._write_section(f, section_name, section_data)

        f.close()
        
        return
            
    ###########################################################################
    # Private interface.
    ###########################################################################

    def _get_file(self, file_or_filename, mode='r'):
        """ Return an open file object from a file or a filename. """

        if isinstance(file_or_filename, basestring):
            f = file(file_or_filename, mode)
                
        else:
            f = file_or_filename

        return f

    def _get_namespace(self, section_name):
        """ Get the namespace that represents the section. """

        components = section_name.split('.')
        namespace = self._namespaces.setdefault(components[0], Namespace())

        for component in components[1:]:
            if not hasattr(namespace, component):
                setattr(namespace, component, Namespace())

            namespace = getattr(namespace, component)

        return namespace
    
    def _parse_section(self, section_name, section_body):
        """ Parse a section.

        In this implementation, we don't actually 'parse' anything - we just
        execute the body of the section as Python code ;^)

        """

        # If this is the first time that we have come across this section then
        # start with an empty dictionary for its contents. Otherwise, we will
        # update the existing contents.
        section = self.setdefault(section_name, {})

        # Execute the Python code in the section dictionary.
        #
        # We use 'self._namespaces' as the globals for the code execution so
        # that config values can refer to other config values.
        #
        # e.g.
        #
        # [acme.foo]
        # bar = 1
        #
        # [acme.baz]
        # blitzel = acme.foo.bar * 2
        exec section_body in self._namespaces, section

        # The '__builtins__' dictionary gets added to the global namespace used
        # in the call to 'exec'. However, we want 'self._namespaces' to only
        # contain 'Namespace' instances, so we do the cleanup here.
        del self._namespaces['__builtins__']

        # Get the section's corresponding node in the 'dotted' namespace.
        namespace = self._get_namespace(section_name)

        # Connect the internals of the node in the 'dotted' namespace to the
        # section!
        namespace.__dict__.update(section)

        return

    def _write_section(self, f, section_name, section_data):
        """ Write a section to a file. """

        f.write('[%s]\n' % section_name)

        for name, value in section_data.items():
            f.write('%s = %s\n' % (name, repr(value)))

        f.write('\n')

        return

    ###########################################################################
    # Debugging interface.
    ###########################################################################

    def _pretty_print_namespaces(self):
        """ Pretty print the 'dotted' namespaces. """

        for name, value in self._namespaces.items():
            print 'Namespace:', name
            value.pretty_print('  ')

        return


###############################################################################
# Internal use only.
###############################################################################

class Namespace(object):
    """ An object that represents a section in a dotted namespace.

    In config files, it is useful for a value to be able to refer to other
    values:-
    
    e.g.

    [acme.foo]
    bar = 1

    [acme.baz]
    blitzel = acme.foo.bar * 2

    These namespace objects are used to build up the 'dotted' namespace so that
    when the body of the section is evaluated, the name 'acme.foo.bar' resolves
    to the appropriate value.

    """

    ###########################################################################
    # Debugging interface.
    ###########################################################################

    def pretty_print(self, indent=''):
        """ Pretty print the namespace. """

        for name, value in self.__dict__.items():
            if isinstance(value, Namespace):
                print indent, 'Namespace:', name
                value.pretty_print(indent + '  ')

            else:
                print indent, name, ':', value

        return
    
#### EOF ######################################################################
