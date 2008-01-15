""" A simple(istic?) Python-esque configuration file. """



class PyConfigFile(dict):
    """ A simple(istic?) Python-esque configuration file. """

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, file_or_filename=None):
        """ Constructor. """

        if file_or_filename is not None:
            self.load(file_or_filename)
        
        return
    
    ###########################################################################
    # 'PyConfigFile' interface.
    ###########################################################################
    
    def load(self, file_or_filename):
        """ Load the configuration from a file.

        'file_or_filename' can be a filename or a file-like object in read
        mode.

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
        
        return

    def save(self, file_or_filename):
        """ Save the configuration to a file.

        'file_or_filename' can be a filename or a file-like object in write
        mode.

        """

        # Get an open file to write to.
        f = self._get_file(file_or_filename, 'w')

        # Write each section to the file.
        for section_name, section_data in self.items():
            f.write('[%s]\n' % section_name)

            for name, value in section_data.items():
                f.write('%s = %s\n' % (name, repr(value)))

            f.write('\n')

        f.close()
        
        return
            
    ###########################################################################
    # Private interface.
    ###########################################################################

    def _parse_section(self, section_name, section_body):
        """ Parse a section. """

        # In this implementation, we don't actually 'parse' anything - we just
        # execute the body of the section as Python code ;^)
        section = self.setdefault(section_name, {})
        
        exec section_body in globals(), section

        return
    
    def _get_file(self, file_or_filename, mode='r'):
        """ Return an open file object from a file or a filename. """

        if isinstance(file_or_filename, basestring):
            f = file(file_or_filename, mode)
                
        else:
            f = file_or_filename

        return f
        
#### EOF ######################################################################
