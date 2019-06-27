"""
Tests for FeedbackMessage model.
"""

import numpy as np
import unittest
from unittest.mock import patch
from PIL import Image

from traits.api import TraitError
from traits.testing.unittest_tools import UnittestTools

from apptools.feedback.feedbackbot.model import FeedbackMessage


class TestFeedbackMessage(unittest.TestCase, UnittestTools):

    def test_invalid_img_data_raises_error(self):
        """ Test that setting img_data to an incorrectly shaped array
            raises a TraitError.

        """

        with self.assertRaises(TraitError):

            FeedbackMessage(img_data=np.empty((2, 2)),
                            token='xoxb-123456',
                            channels='#general')

    def test_invalid_channel_raises_error(self):
        """ Test that passing a channel name that doesn't begin with
            '#' raises TraitError.

        """

        with self.assertRaises(TraitError):

            FeedbackMessage(img_data=np.empty((1, 1, 3)),
                            token='xoxb-123456',
                            channels='general')

    def test_send(self):
        """ Test that the slack client call happens with the correct arguments.

        """

        img_data = np.array([[[1, 2, 3]]], dtype=np.uint8)

        token = 'xoxb-123456'

        channels = '#general'

        msg = FeedbackMessage(img_data=img_data,
                              token=token,
                              channels=channels)

        msg.name = 'Tom Riddle'
        msg.organization = 'Death Eather, Inc'
        msg.description = 'No one calls me Voldy.'

        expected_msg = 'Name: {}\nOrganization: {}\nDescription: {}'.format(
            msg.name, msg.organization, msg.description)

        files_upload_found = False

        with patch('apptools.feedback.feedbackbot.model.slack'):

            with patch('apptools.feedback.feedbackbot.model.slack.WebClient') \
                    as mock_client:

                msg.send()

                for call_ in mock_client.mock_calls:
                    # Loop over all calls made to mock_client, including nested
                    # function calls.

                    # Glean function name, provided positional and keyword
                    # arguments in call_
                    name, args, kwargs = call_

                    if name == '().files_upload':

                        files_upload_found = True

                        # The following lines ensure that <files_upload> is
                        # called with the correct arguments.

                        # There shouldn't be any positional arguments.
                        self.assertTupleEqual((), args)

                        # The following lines check whether keyword arguments
                        # were passed correctly.
                        np.testing.assert_almost_equal(
                            img_data, np.array(Image.open(kwargs['file'])))

                        self.assertEqual(channels, kwargs['channels'])

                        self.assertEqual(
                            expected_msg, kwargs['initial_comment'])

                if not files_upload_found:

                    self.fail(
                        "Call to Slack API method <files_upload> not found.")


if __name__ == '__main__':

    unittest.main()
