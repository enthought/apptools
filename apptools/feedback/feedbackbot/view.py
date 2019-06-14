"""
This model implements UI classes and logic for a plugin that enables 
clients to send feedback messages to a developer team's slack channel.
"""

import numpy as np
from traits.api import Property, Instance
from traitsui.api import (
        View, Group, Item, Action, 
        Label, Controller)
from traitsui.menu import CancelButton 
from chaco.api import Plot, ArrayPlotData
from enable.api import ComponentEditor
from enable.primitives.image import Image

from .model import FeedbackMessage

# ----------------------------------------------------------------------------
# TraitsUI Actions 
# ----------------------------------------------------------------------------

send_button = Action(name='Send', action='send', 
    enabled_when='controller._send_enabled')

# ----------------------------------------------------------------------------
# TraitsUI Views
# ----------------------------------------------------------------------------

#: Primary view for the feedback message.
feedback_msg_view = View(
    Label('Enter feedback here. All fields are mandatory.'),
    Group(
        Group(
            Item('first_name'),
            Item('last_name'),
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

    model = Instance(FeedbackMessage)

    image_component = Instance(Image)

    #: Property that decides whether the state of the message is valid 
    # for sending.
    _send_enabled = Property(depends_on='[+msg_meta]')

    trait_view = feedback_msg_view

    def _image_component_default(self):

        return Image(data=self.model.img_data)

    def _get__send_enabled(self):
        """ Logic to check if message is valid for sending. """

        return self.model.first_name and self.model.last_name \
           and self.model.organization and self.model.description 

