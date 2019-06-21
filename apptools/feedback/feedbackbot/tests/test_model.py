"""
Tests for FeedbackMessage model.
"""

import numpy as np
import unittest

from traits.api import TraitError
from traits.testing.unittest_tools import UnittestTools

from apptools.feedback.feedbackbot.model import FeedbackMessage

class TestFeedbackMessage(unittest.TestCase, UnittestTools):

    def test_invalid_img_data_raises_error(self):
        """ Test that setting img_data to an incorrectly shaped array 
            raises a TraitError.

        """

        with self.assertRaises(TraitError):

            msg = FeedbackMessage(img_data=np.empty((2,2)), 
                    token='xoxb-123456', channels='#general')

    def test_invalid_channel_raises_error(self):
        """ Test that passing a channel name that doesn't begin with 
            '#' raises TraitError.

        """

        with self.assertRaises(TraitError):
        
            msg = FeedbackMessage(img_data=np.empty((1,1,3)),
                token='xoxb-123456', channels='general')


if __name__ == '__main__':

    unittest.main()
