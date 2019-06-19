"""
This model implements UI classes and logic for a plugin that enables 
clients to send feedback messages to a developer team's slack channel.
"""

import sys
import traceback

import slack
import numpy as np
import aiohttp
from traits.api import Property, Instance
from traitsui.api import (
        View, Group, Item, Action, 
        Label, Controller)
from traitsui.menu import CancelButton 
from chaco.api import Plot, ArrayPlotData
from enable.api import ComponentEditor
from enable.primitives.image import Image as ImageComponent
from pyface.api import confirm, information, warning, error, YES, NO

from .model import FeedbackMessage

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
    resizable=True)


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

        # Variable to store whether to let the client-user try again if Slack rate limits
        # the bot, or if the request takes too long.
        retry = False

        try:

            response = self.model.send()

        except slack.errors.SlackApiError as exc:

            # Allow the client-user to try again if rate limited by Slack, 
            # or if the HTTP request to Slack takes too long. The rate
            # limit for this API call is around 20 requests per workspace per
            # minute. It is unlikely that this will happen, but no harm in
            # handling it.
            if exc.response["error"] == "ratelimited":

                    retry_time = exc.response.headers["retry-after"]

                    err_msg = "Server received too many requests." \
                        + " Please try again after {} seconds.".format(retry_time)

                    retry = True

            else:

                err_msg = 'Message sent successfully, but received an error' \
                    + ' response from Slack.'
            
            error(ui_info.ui.control, err_msg, detail=str(exc))

        except aiohttp.ServerTimeoutError as exc:

            err_msg = 'Server took too long to respond. Please try again later.'

            error(ui_info.ui.control, err_msg, detail=str(exc))

            retry = True

        except aiohttp.ClientConnectionError as exc:

            err_msg = 'An error occured while connecting to the server.'

            error(ui_info.ui.control, err_msg, detail=str(exc))

        except Exception as exc:

            err_msg = 'Unexpected error: {}'.format(str(exc))

            detail = ' '.join(traceback.format_tb(exc.__traceback__))

            error(ui_info.ui.control, err_msg, detail=detail)

        else:

            success_msg = 'Message sent successfully.'

            information(ui_info.ui.control, success_msg)

        finally:

            # Kill the GUI if the user will not retry.
            if not retry:
                ui_info.ui.dispose()

