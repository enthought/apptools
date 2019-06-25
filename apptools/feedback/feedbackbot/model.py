"""
This module implements a class that provides logic for a simple plugin
for sending messages to a developer team's slack channel.
"""

import io
import logging

import slack
from PIL import Image

from traits.api import (
    HasRequiredTraits, Str, Property, Array, String)

logger = logging.getLogger(__name__)


class FeedbackMessage(HasRequiredTraits):
    """ Model for the feedback message.

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
    channels = String(minlen=2, regex='#.*', required=True)

    #: OAuth token for the slackbot, must be provided by the user-developer.
    token = Str(required=True)

    #: The final message that gets posted to Slack.
    msg = Property(Str, depends_on='+msg_meta')

    #: 3D numpy array to hold three channel (RGB) screenshot pixel data.
    img_data = Array(shape=(None, None, 3), dtype='uint8', required=True)

    def _get_msg(self):

        feedback_template = 'Name: {name}\n' \
            + 'Organization: {org}\nDescription: {desc}'

        return feedback_template.format(
            name=self.name,
            org=self.organization,
            desc=self.description)

    def send(self):
        """ Send feedback message and screenshot to Slack. """

        # Set up object that talks to Slack's API. Note that the run_async
        # flag is False. This ensures that each HTTP request is blocking. More
        # precisely, the WebClient sets up an event loop with just a single
        # HTTP request in it, and ensures that the event loop runs to
        # completion before returning.
        client = slack.WebClient(token=self.token,
                                 timeout=5,
                                 ssl=True,
                                 run_async=False)

        logger.info("Attempting to send message: <%s> to channel: <%s>",
                    self.msg, self.channels)

        # Compress screenshot into PNG format using an in-memory buffer.
        compressed_img_buf = io.BytesIO()

        Image.fromarray(self.img_data).save(compressed_img_buf, 'PNG')

        compressed_img_buf.seek(0)

        # Send message.
        response = client.files_upload(
                channels=self.channels,
                initial_comment=self.msg,
                filetype='png',
                filename='screenshot.png',
                file=compressed_img_buf)

        logger.info("Message sent."
                    + " Slack responded with OK : {ok_resp}".format(
                        ok_resp=response['ok']))

        return response
