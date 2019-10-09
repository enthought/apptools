from email.mime.multipart import MIMEMultipart
import unittest

try:
    # On Python 3, mock is part of the standard library,
    from unittest import mock
except ImportError:
    # Whereas on Python 2 it is not.
    import mock

from apptools.logger.plugin.logger_service import LoggerService


class LoggerServiceTestCase(unittest.TestCase):
    def test_create_email_message(self):
        logger_service = LoggerService()
        with mock.patch.object(logger_service, 'whole_log_text')\
                as mocked_log_txt:
            mocked_log_txt.return_value = "Dummy log data"
            msg = logger_service.create_email_message(
                fromaddr='', toaddrs='', ccaddrs='', subject='', priority=''
            )
        self.assertIsInstance(msg, MIMEMultipart)

    def test_create_email_message_with_user_data(self):
        # We used a mocked logger service which doesn't depend on the
        # application trait and the presence of extensions to the extension
        # point `apptools.logger.plugin.mail_files`
        class MockedLoggerService(LoggerService):
            def _get_mail_files(self):
                return [lambda zip_file : None]

        logger_service = MockedLoggerService()
        with mock.patch.object(logger_service, 'whole_log_text')\
                as mocked_log_txt:
            mocked_log_txt.return_value = "Dummy log data"
            msg = logger_service.create_email_message(
                fromaddr='', toaddrs='', ccaddrs='', subject='', priority='',
                include_userdata=True,
            )
        self.assertIsInstance(msg, MIMEMultipart)
