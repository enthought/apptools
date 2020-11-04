from email.mime.multipart import MIMEMultipart
import io
import os
import shutil
import tempfile
import unittest

try:
    # On Python 3, mock is part of the standard library,
    from unittest import mock
except ImportError:
    # Whereas on Python 2 it is not.
    import mock

from apptools.logger.agent.attachments import Attachments


class AttachmentsTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir)

        self.tmpfile = os.path.join(self.tmpdir, "dummy_file.txt")
        with io.open(self.tmpfile, 'w', encoding='utf8') as filehandle:
            filehandle.write(u"Dummy data in dummy file for dummies")

    def test_attaching_workspace(self):
        class DummyWorkspace(object):
            path = self.tmpdir

        class MockedApplication(object):
            tmpdir = self.tmpdir
            def get_service(self, service_id):
                return DummyWorkspace()

        attachments = Attachments(
            application=MockedApplication(),
            message=MIMEMultipart()
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
            application=MockedApplication(),
            message=MIMEMultipart()
        )
        attachments.package_single_project()

        message = attachments.message
        self.assertTrue(message.is_multipart())
        payload = message.get_payload()
        self.assertEqual(len(payload), 1)
