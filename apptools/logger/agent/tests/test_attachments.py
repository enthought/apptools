# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
from email.mime.multipart import MIMEMultipart
import io
import os
import shutil
import tempfile
import unittest

from apptools.logger.agent.attachments import Attachments


class AttachmentsTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir)

        self.tmpfile = os.path.join(self.tmpdir, "dummy_file.txt")
        with io.open(self.tmpfile, "w", encoding="utf8") as filehandle:
            filehandle.write("Dummy data in dummy file for dummies")

    def test_attaching_workspace(self):
        class DummyWorkspace(object):
            path = self.tmpdir

        class MockedApplication(object):
            tmpdir = self.tmpdir

            def get_service(self, service_id):
                return DummyWorkspace()

        attachments = Attachments(
            application=MockedApplication(), message=MIMEMultipart()
        )
        attachments.package_workspace()

        message = attachments.message
        self.assertTrue(message.is_multipart())
        payload = message.get_payload()
        self.assertEqual(len(payload), 1)

    def test_attaching_single_project(self):
        class DummySingleProject(object):
            location = self.tmpdir

        class MockedApplication(object):
            tmpdir = self.tmpdir

            def get_service(self, service_id):
                return DummySingleProject()

        attachments = Attachments(
            application=MockedApplication(), message=MIMEMultipart()
        )
        attachments.package_single_project()

        message = attachments.message
        self.assertTrue(message.is_multipart())
        payload = message.get_payload()
        self.assertEqual(len(payload), 1)
