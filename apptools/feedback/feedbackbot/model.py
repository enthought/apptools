"""
This module implements a class that provides logic for a simple plugin
for sending messages to a developer team's slack channel.
"""

import io

import numpy as np
import slack
import aiohttp
from PIL import Image

from traits.api import (
        HasTraits, Str, Property,
        Int, Array, Bytes, String,
        Any, cached_property, on_trait_change)


class FeedbackMessage(HasTraits):
    """Model for the feedback message.

    Notes
    -----
    The user-developer must specify the slack channel that the message must be
    sent to, as well as provide raw screenshot data.

    """

    #: Name of the client user
    name = Str(msg_meta=True)

    #: Name of the client organization.
    organization = Str(msg_meta=True)

    # TODO: Slack supports some markdown in messages, provide
    # some details here.
    #: Main body of the feedback message.
    description = Str(msg_meta=True)

    #: The target slack channel that the bot will post to, must start with # 
    # and must be provided by the user-developer.
    channels = String(minlen=2, regex='#.*')

    #: OAuth token for the slackbot, must be provided by the user-developer.
    token = Str

    #: The final slack message that will be posted.
    msg = Property(Str, depends_on='msg_meta')

    #: 3D numpy array to hold three channel (RGB) screenshot pixel data.
    img_data = Array(shape=(None, None, 3), dtype='uint8')
    
    def _get_msg(self):

        feedback_template = 'Name: {name}\n' \
            + 'Organization: {org}\nDescription: {desc}'

        return  feedback_template.format(
            name=self.name, 
            org=self.organization, 
            desc=self.description)

    def send(self):
        """ Send feedback message and screenshot to slack. """

        # Set up object that talks to Slack's API. Note that the run_async  
        # flag is False. This ensures that each HTTP request is blocking. More
        # precisely, the WebClient sets up an event loop with just a single
        # HTTP request in it, and ensures that the event loop runs to
        # completion before returning. 
        client = slack.WebClient(token=self.token,
                                 timeout=5,
                                 ssl=True, 
                                 run_async=False)

        # Compress image into PNG format using an in-memory buffer.
        buf = io.BytesIO()
        Image.fromarray(self.img_data).save(buf, 'PNG')
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
 
