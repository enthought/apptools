"""
This module implements UI classes and logic for a plugin that enables 
clients to send feedback messages to a developer team's slack channel.
"""

import sys
import logging
import traceback

import slack
import numpy as np
import aiohttp

from traits.api import Property, Instance
from traitsui.api import (
        View, Group, Item, Action, 
        Label, Controller, Handler)
from traitsui.menu import CancelButton 
from chaco.api import Plot, ArrayPlotData
from enable.api import ComponentEditor
from enable.primitives.image import Image as ImageComponent
from pyface.api import confirm, information, warning, error, YES, NO

from .model import FeedbackMessage

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# TraitsUI Actions 
# ----------------------------------------------------------------------------

send_button = Action(name='Send', action='_do_send', 
    enabled_when='controller._send_enabled')

# ----------------------------------------------------------------------------
# TraitsUI Views
# ----------------------------------------------------------------------------

#: Primary view for the feedback message.
feedback_msg_view = View(
    Label('Enter feedback here. All fields are mandatory.'),
    Group(
        Group(
            Item('name'),
            Item('organization', 
                 tooltip='Enter the name of your organization.'),
            Item('description', 
                 tooltip='Enter feedback.',
                 height=200,
                 springy=True)),
        Group(
            Item('controller.image_component',
                 editor=ComponentEditor(),
                 show_label=False)),
        orientation='horizontal'),
    buttons=[CancelButton, send_button],
    width=800,
    resizable=True,
    title='Feedback Reporter')


# ----------------------------------------------------------------------------
# TraitsUI Handler
# ----------------------------------------------------------------------------

class FeedbackController(Controller):
    """Controller for FeedbackMessage.

    The Controller allows the client user to specify the feedback and preview 
    the screenshot.

    """

    #: The underlying model.
    model = Instance(FeedbackMessage)

    #: Enable component to store the screenshot.
    image_component = Instance(ImageComponent)

    #: Property that decides whether the state of the message is valid 
    # for sending.
    _send_enabled = Property(depends_on='[+msg_meta]')

    # Default view for this controller.
    trait_view = feedback_msg_view

    def _image_component_default(self):
        """ Default image to display, this is simply the screenshot."""

        return ImageComponent(data=self.model.img_data)
    
    def _get__send_enabled(self):
        """ Logic to check if message is valid for sending. """

        return self.model.name \
           and self.model.organization and self.model.description 

    def _do_send(self, ui_info):
        """ Actions to perform when the send button is clicked. """

        logger.info('Send button clicked in feedback dialog box.')

        # Boolean that specifies whether the client-user can try again or not.
        # If False, then the feedback dialog box is automatically closed. 
        # If True, the feedback dialog is kept alive. A possible use case could
        # arise when the request to the Slack API takes too long (in which case
        # an aiohttp.ServerTimeoutError is raised). In that case, notify the
        # user of the error, but keep the dialog box alive. This way, the data
        # that the client-user enters persists, allowing them to try sending it
        # again without more typing. The other possible use case is when Slack
        # rate-limits the bot.
        retry = False

        try:

            response = self.model.send()

        except slack.errors.SlackApiError as exc:

            if exc.response["error"] == "ratelimited":
                # Slack has rate-limited the bot.
                # The rate limit for this API call is around 20 requests per 
                # workspace per minute. It is unlikely that this will happen, 
                # but no harm in handling it.

                # Slack promises to return a retry-after value in seconds in
                # the response headers.
                retry_time = exc.response.headers["retry-after"]

                err_msg = "Server received too many requests." \
                    + " Please try again after {} seconds.".format(retry_time)

                # Allow the user the opportunity to retry the send operation.
                retry = True

            else:
                # All other Slack API errors (invalid_auth, invalid_channel,
                # etc.)

                err_msg = 'Message sent successfully, but received an error' \
                    + ' response from Slack.'
            
            # Construct the detail message explicitly instead of simply calling
            # str(exc), which in some cases can reveal the OAuth token.
            detail = 'Slack response: <ok : {ok_resp}, error : {err_resp}>'.format(
                ok_resp=exc.response['ok'], err_resp=exc.response['error'])
            
            error(ui_info.ui.control, err_msg, detail=detail)

            # For the same reason (str(exc) can reveal the OAuth token)
            # use logger.error instead of logger.exception
            logger.error(err_msg + ' ' + detail) 

        except aiohttp.ServerTimeoutError as exc:

            err_msg = 'Server took too long to respond. Please try again later.'

            error(ui_info.ui.control, err_msg, detail=str(exc))

            retry = True

            logger.exception(err_msg)

        except aiohttp.ClientConnectionError as exc:
            # Handle all client-related connection errors raised by aiohttp
            # here.

            err_msg = 'An error occured while connecting to the server.'

            error(ui_info.ui.control, err_msg, detail=str(exc))

            logger.exception(err_msg)

        except Exception as exc:
            # Handle all other exceptions here.

            err_msg = 'Unexpected error: {}'.format(str(exc))

            detail = ' '.join(traceback.format_tb(exc.__traceback__))

            error(ui_info.ui.control, err_msg, detail=detail)

            logger.exception(err_msg)

        else:

            success_msg = 'Message sent successfully.'

            information(ui_info.ui.control, success_msg)

        finally:

            # Kill the GUI if the user will not retry.
            if not retry:

                ui_info.ui.dispose()

                logger.info('Feedback dialog closed automatically.')

