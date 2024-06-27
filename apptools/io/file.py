# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" A representation of files and folders in a file system. """


# Standard/built-in imports.
import mimetypes
import os
import shutil
import stat

# Enthought library imports.
from traits.api import Bool, HasPrivateTraits, Instance, List, Property
from traits.api import Str


class File(HasPrivateTraits):
    """ A representation of files and folders in a file system. """

    #### 'File' interface #####################################################

    # The absolute path name of this file/folder.
    absolute_path = Property(Str)

    # The folder's children (for files this is always None).
    children = Property(List("File"))

    # The file extension (for folders this is always the empty string).
    #
    # fixme: Currently the extension includes the '.' (ie. we have '.py' and
    # not 'py'). This is because things like 'os.path.splitext' leave the '.'
    # on, but I'm not sure that this is a good idea!
    ext = Property(Str)

    # Does the file/folder exist?
    exists = Property(Bool)

    # Is this an existing file?
    is_file = Property(Bool)

    # Is this an existing folder?
    is_folder = Property(Bool)

    # Is this a Python package (ie. a folder contaning an '__init__.py' file.
    is_package = Property(Bool)

    # Is the file/folder readonly?
    is_readonly = Property(Bool)

    # The MIME type of the file (for a folder this will always be
    # 'context/unknown' (is that what it should be?)).
    mime_type = Property(Str)

    # The last component of the path without the extension.
    name = Property(Str)

    # The parent of this file/folder (None if it has no parent).
    parent = Property(Instance("File"))

    # The path name of this file/folder.
    path = Str

    # A URL reference to the file.
    url = Property(Str)

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, path, **traits):
        """ Creates a new representation of the specified path. """

        super(File, self).__init__(path=path, **traits)

    def __str__(self):
        """ Returns an 'informal' string representation of the object. """

        return "File(%s)" % self.path

    ###########################################################################
    # 'File' interface.
    ###########################################################################

    #### Properties ###########################################################

    def _get_absolute_path(self):
        """ Returns the absolute path of this file/folder. """

        return os.path.abspath(self.path)

    def _get_children(self):
        """Returns the folder's children.

        Returns None if the path does not exist or is not a folder.

        """

        if self.is_folder:
            children = []
            for name in os.listdir(self.path):
                children.append(File(os.path.join(self.path, name)))

        else:
            children = None

        return children

    def _get_exists(self):
        """ Returns True if the file exists, otherwise False. """

        return os.path.exists(self.path)

    def _get_ext(self):
        """ Returns the file extension. """

        name, ext = os.path.splitext(self.path)

        return ext

    def _get_is_file(self):
        """ Returns True if the path exists and is a file. """

        return self.exists and os.path.isfile(self.path)

    def _get_is_folder(self):
        """ Returns True if the path exists and is a folder. """

        return self.exists and os.path.isdir(self.path)

    def _get_is_package(self):
        """ Returns True if the path exists and is a Python package. """

        return self.is_folder and "__init__.py" in os.listdir(self.path)

    def _get_is_readonly(self):
        """ Returns True if the file/folder is readonly, otherwise False. """

        # If the File object is a folder, os.access cannot be used because it
        # returns True for both read-only and writable folders on Windows
        # systems.
        if self.is_folder:

            # Mask for the write-permission bits on the folder. If these bits
            # are set to zero, the folder is read-only.
            WRITE_MASK = 0x92
            permissions = os.stat(self.path)[0]

            if permissions & WRITE_MASK == 0:
                readonly = True
            else:
                readonly = False

        elif self.is_file:
            readonly = not os.access(self.path, os.W_OK)

        else:
            readonly = False

        return readonly

    def _get_mime_type(self):
        """ Returns the mime-type of this file/folder. """

        mime_type, encoding = mimetypes.guess_type(self.path)
        if mime_type is None:
            mime_type = "content/unknown"

        return mime_type

    def _get_name(self):
        """ Returns the last component of the path without the extension. """

        basename = os.path.basename(self.path)

        name, ext = os.path.splitext(basename)

        return name

    def _get_parent(self):
        """ Returns the parent of this file/folder. """

        return File(os.path.dirname(self.path))

    def _get_url(self):
        """ Returns the path as a URL. """

        # Strip out the leading slash on POSIX systems.
        return "file:///%s" % self.absolute_path.lstrip("/")

    #### Methods ##############################################################

    def copy(self, destination):
        """ Copies this file/folder. """

        # Allow the destination to be a string.
        if not isinstance(destination, File):
            destination = File(destination)

        if self.is_folder:
            shutil.copytree(self.path, destination.path)

        elif self.is_file:
            shutil.copyfile(self.path, destination.path)

    def create_file(self, contents=""):
        """ Creates a file at this path. """

        if self.exists:
            raise ValueError("file %s already exists" % self.path)

        f = open(self.path, "w")
        f.write(contents)
        f.close()

    def create_folder(self):
        """Creates a folder at this path.

        All intermediate folders MUST already exist.

        """

        if self.exists:
            raise ValueError("folder %s already exists" % self.path)

        os.mkdir(self.path)

    def create_folders(self):
        """Creates a folder at this path.

        This will attempt to create any missing intermediate folders.

        """

        if self.exists:
            raise ValueError("folder %s already exists" % self.path)

        os.makedirs(self.path)

    def create_package(self):
        """Creates a package at this path.

        All intermediate folders/packages MUST already exist.

        """

        if self.exists:
            raise ValueError("package %s already exists" % self.path)

        os.mkdir(self.path)

        # Create the '__init__.py' file that actually turns the folder into a
        # package!
        init = File(os.path.join(self.path, "__init__.py"))
        init.create_file()

    def delete(self):
        """Deletes this file/folder.

        Does nothing if the file/folder does not exist.

        """

        if self.is_folder:
            # Try to make sure that everything in the folder is writeable.
            self.make_writeable()

            # Delete it!
            shutil.rmtree(self.path)

        elif self.is_file:
            # Try to make sure that the file is writeable.
            self.make_writeable()

            # Delete it!
            os.remove(self.path)

    def make_writeable(self):
        """ Attempt to make the file/folder writeable. """

        if self.is_folder:
            # Try to make sure that everything in the folder is writeable
            # (i.e., can be deleted!).  This comes in especially handy when
            # deleting '.svn' directories.
            for path, dirnames, filenames in os.walk(self.path):
                for name in dirnames + filenames:
                    filename = os.path.join(path, name)
                    if not os.access(filename, os.W_OK):
                        os.chmod(filename, stat.S_IWUSR)

        elif self.is_file:
            # Try to make sure that the file is writeable (i.e., can be
            # deleted!).
            if not os.access(self.path, os.W_OK):
                os.chmod(self.path, stat.S_IWUSR)

    def move(self, destination):
        """ Moves this file/folder. """

        # Allow the destination to be a string.
        if not isinstance(destination, File):
            destination = File(destination)

        # Try to make sure that everything in the directory is writeable.
        self.make_writeable()

        # Move it!
        shutil.move(self.path, destination.path)
