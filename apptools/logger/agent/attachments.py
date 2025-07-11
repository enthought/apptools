# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
""" Attach relevant project files.

FIXME: there are no public project plugins for Envisage 3, yet. In any case,
this stuff should not be hard-coded, but extensible via extension points. The
code remains here because we can reuse the zip utility code in that extensible
rewrite.
"""

import logging
import os.path
from email import encoders
from email.mime.base import MIMEBase

from traits.api import Any, HasTraits


logger = logging.getLogger(__name__)


class Attachments(HasTraits):

    application = Any()
    message = Any()

    def __init__(self, message, **traits):
        traits = traits.copy()
        traits["message"] = message
        super(Attachments, self).__init__(**traits)

    # FIXME: all of the package_*() methods refer to deprecated project plugins

    def package_workspace(self):
        if self.application is None:
            pass

        workspace = self.application.get_service("envisage.project.IWorkspace")
        if workspace is not None:
            dir = workspace.path
            self._attach_directory(dir)

    def package_single_project(self):
        if self.application is None:
            pass

        single_project = self.application.get_service(
            "envisage.single_project.ModelService"
        )
        if single_project is not None:
            dir = single_project.location
            self._attach_directory(dir)

    def package_any_relevant_files(self):
        self.package_workspace()
        self.package_single_project()

    def _attach_directory(self, dir):
        relpath = os.path.basename(dir)

        import zipfile
        from io import BytesIO

        ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        msg = MIMEBase(maintype, subtype)

        file_object = BytesIO()
        zip = zipfile.ZipFile(file_object, "w")
        _append_to_zip_archive(zip, dir, relpath)
        zip.close()

        msg.set_payload(file_object.getvalue())

        encoders.encode_base64(msg)  # Encode the payload using Base64
        msg.add_header(
            "Content-Disposition", "attachment", filename="project.zip"
        )

        self.message.attach(msg)

        file_object.close()


def _append_to_zip_archive(zip, dir, relpath):
    """ Add all files in and below directory dir into zip archive"""
    for filename in os.listdir(dir):
        path = os.path.join(dir, filename)

        if os.path.isfile(path):
            name = os.path.join(relpath, filename)
            zip.write(path, name)
            logger.debug("adding %s to error report" % path)
        else:
            if filename != ".svn":  # skip svn files if any
                subdir = os.path.join(dir, filename)
                _append_to_zip_archive(
                    zip, subdir, os.path.join(relpath, filename)
                )
