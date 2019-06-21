"""
Tests for FeedbackController.
"""

import unittest
from unittest.mock import patch, MagicMock, create_autospec

import numpy as np
from aiohttp import ClientConnectionError, ServerTimeoutError
from slack.errors import SlackApiError

from traits.testing.unittest_tools import UnittestTools
from traitsui.api import UIInfo

from apptools.feedback.feedbackbot.model import FeedbackMessage
from apptools.feedback.feedbackbot.view import FeedbackController


class TestFeedbackController(unittest.TestCase, UnittestTools):

    def setUp(self):

        self.msg = FeedbackMessage(img_data=np.empty((2, 2, 3)),
                                   channels='#dummy',
                                   token='xoxb-123456')

        self.msg.name = 'dummy_name'
        self.msg.organization = 'dummy_org'
        self.msg.description = 'dummy_desc'

    def test__send_enabled_empty_name(self):
        """ Test send button is disabled if name is empty. """

        self.msg.name = ''

        controller_no_name = FeedbackController(model=self.msg)

        self.assertFalse(controller_no_name._send_enabled)

    def test__send_enabled_empty_organization(self):
        """ Test send button is disabled if organization is empty. """

        self.msg.organization = ''

        controller_no_organization = FeedbackController(model=self.msg)

        self.assertFalse(controller_no_organization._send_enabled)

    def test__send_enabled_empty_description(self):
        """ Test send button is disabled if description is empty. """

        self.msg.description = ''

        controller_no_description = FeedbackController(model=self.msg)

        self.assertFalse(controller_no_description._send_enabled)

    def test_error_dialog_opened_if_slack_ratelimited_exception_occurs(self):
        """ Test that an error dialog box is opened if a SlackApiError occurs
            as a result of being rate-limited.

        """

        # Patch the slack.web.slack_response.SlackResponse object. If
        # a rate-limited error occurs, Slack promises it will return
        # a retry-after header in the respones, so add that to the mock
        # instance as well.
        dummy_response = MagicMock(
                data=patch.dict({'ok': False, 'error': 'ratelimited'}),
                headers={'retry-after': 10})

        self.msg.__dict__['send'] = MagicMock(
            side_effect=SlackApiError('msg', dummy_response))

        controller = FeedbackController(model=self.msg)

        with patch('apptools.feedback.feedbackbot.view.error') as mock_error:

            controller._do_send(create_autospec(UIInfo()))

            mock_error.assert_called_once()

    def test_error_dialog_opened_if_slack_exception_occurs(self):
        """ Test that an error dialog box is opened if a SlackApiError occurs,
            but not as a result of being rate-limited.

        """

        dummy_response = MagicMock(
                data=patch.dict({'ok': False, 'error': 'dummy_error'}))

        self.msg.__dict__['send'] = MagicMock(
            side_effect=SlackApiError('msg', dummy_response))

        controller = FeedbackController(model=self.msg)

        with patch('apptools.feedback.feedbackbot.view.error') as mock_error:

            controller._do_send(create_autospec(UIInfo()))

            mock_error.assert_called_once()

    def test_error_dialog_opened_if_client_connection_exception_occurs(self):
        """ Test that an error dialog box is opened if a ClientConnectionError
            occurs.

        """

        self.msg.__dict__['send'] = MagicMock(
            side_effect=ClientConnectionError)

        controller = FeedbackController(model=self.msg)

        with patch('apptools.feedback.feedbackbot.view.error') as mock_error:

            controller._do_send(create_autospec(UIInfo()))

            mock_error.assert_called_once()

    def test_error_dialog_opened_if_server_timeout_exception_occurs(self):
        """ Test that an error dialog box is opened if a ServerTimeoutError
            occurs.

        """

        self.msg.__dict__['send'] = MagicMock(
            side_effect=ServerTimeoutError)

        controller = FeedbackController(model=self.msg)

        with patch('apptools.feedback.feedbackbot.view.error') as mock_error:

            controller._do_send(create_autospec(UIInfo()))

            mock_error.assert_called_once()

    def test_error_dialog_opened_if_other_exception_occurs(self):
        """ Test that an error dialog box is opened if an Exception
            occurs.

        """

        self.msg.__dict__['send'] = MagicMock(side_effect=Exception)

        controller = FeedbackController(model=self.msg)

        with patch('apptools.feedback.feedbackbot.view.error') as mock_error:

            controller._do_send(create_autospec(UIInfo()))

            mock_error.assert_called_once()

    def test_information_dialog_opened_if_no_exception_occurs(self):
        """ Test that an information dialog box is opened
            if no Exception occurs.

        """

        self.msg.__dict__['send'] = MagicMock()

        controller = FeedbackController(model=self.msg)

        with patch('apptools.feedback.feedbackbot.view.information') \
                as mock_info:

            controller._do_send(create_autospec(UIInfo()))

            mock_info.assert_called_once()


if __name__ == '__main__':

    unittest.main()
