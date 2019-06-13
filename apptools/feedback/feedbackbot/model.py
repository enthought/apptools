"""
This module implements a class that provides logic for a simple plugin
for sending messages to a developer team's slack channel.
"""

import os
import io

import numpy as np
import slack
import aiohttp
from PIL import Image
from traits.api import (
        HasTraits, Str, Property,
        Int, Array, Bytes, String,
        cached_property, on_trait_change)


class FeedbackMessage(HasTraits):
    """Model for the feedback message.

    Notes
    -----
    The user-developer must specify the slack channel that the message must be
    sent to, as well as provide raw screenshot data.

    TODO:
    Add service that reveals OAUTH token.
    """

    first_name = Str(msg_meta=True)

    last_name = Str(msg_meta=True)

    #: Name of the client organization.
    organization = Str(msg_meta=True)

    # TODO: Slack supports some markdown in messages, provide
    # some details here.
    #: Main body of the feedback message.
    description = Str(msg_meta=True)

    #: The target slack channel that the bot will post to, must start with #.
    channels = String(minlen=2, regex='#.*')

    #: The final slack message that will be posted.
    msg = Str

    #: The screenshot pixel data in raw bytes.
    img_bytes = Bytes

    #: The screenshot RGB data as a numeric array.
    img_data = Property(Array)

    #: The screenshot width in pixels.
    img_w = Int 

    #: The screenshot height in pixels.
    img_h = Int

    @cached_property
    def _get_img_data(self):
        """ Compute RGB data from raw image bytes. 

        Returns
        -------
        numpy.ndarray
            RGB values in a numpy ndarray of shape 
            (self.img_h, self.img_w, 3).

        """

        # TODO: assume RGB ordering and provide helper functions to change the
        # order if necessary
        #  [2::-1] is required to order the channels as RGB
        return np.frombuffer(
            self.img_bytes, dtype=np.uint8).reshape((
                self.img_h, 
                self.img_w, -1))[..., 2::-1]

    @on_trait_change('+msg_meta')
    def _update_msg(self):

        feedback_template = 'Name: {first} {last}\n' \
            + 'Organization: {org}\nDescription: {desc}'

        self.msg = feedback_template.format(
            first=self.first_name,
            last=self.last_name, 
            org=self.organization, 
            desc=self.description)

    def send(self):
        """ Send feedback message and screenshot to slack. """

        # TODO: OAuth token should be revealed after client 
        # user credentials are  presented
        # Initialize slack client
        client = slack.WebClient(token=os.environ['FEEDBACKBOT_OAUTH_TOKEN'],
                                 timeout=10,
                                 ssl=True)

        # Compress image into PNG format using an in-memory buffer.
        img = Image.fromarray(self.img_data, mode='RGB')

        buf = io.BytesIO()

        img.save(buf, 'PNG')
        buf.seek(0)

        try:

            # Send message.
            response = client.files_upload(
                    channels=self.channels,
                    initial_comment=self.msg,
                    filetype='png',
                    filename='screenshot.png',
                    file=buf)

        except slack.errors.SlackApiError as error:

            print(
                'Message sent successfully,'
                + ' but received the following error from Slack:')
            print(error)
            raise

        except aiohttp.client_exceptions.ClientConnectorError as error:

            print('Message not sent.')
            print(error)
            raise

        else:

            print('Message sent successfully!')
 
