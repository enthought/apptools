"""
This model implements UI classes and logic for a plugin that enables 
clients to send feedback messages to a developer team's slack channel.
"""

from traits.api import Property, Instance
from traitsui.api import (
        View, Group, Item, Action, 
        Label, Controller)
from traitsui.menu import CancelButton 
from chaco.api import Plot, ArrayPlotData
from enable.api import ComponentEditor

from .model import FeedbackMessage
from .utils import bytes_to_matrix

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
            Item('controller.screenshot_plot',
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

    #: Chaco plot to display the screenshot.
    screenshot_plot = Instance(Plot)

    #: Property that decides whether the state of the message is valid 
    # for sending.
    _send_enabled = Property(depends_on='[+msg_meta]')

    trait_view = feedback_msg_view

    def _screenshot_plot_default(self):
        """ Plots screenshot in Chaco from RGB data. """

        # Reverse rows of model.img_data so that the img_plot looks right

        img_data = bytes_to_matrix(
            self.model.img_bytes, self.model.img_h, self.model.img_w)

        plotdata = ArrayPlotData(img_data=img_data[::-1, ...])
        plot = Plot(plotdata)
        plot.img_plot('img_data', hide_grids=True)

        plot.border_visible = False
        plot.x_axis = None
        plot.y_axis = None

        return plot

    def _get__send_enabled(self):
        """ Logic to check if message is valid for sending. """

        return self.model.first_name and self.model.last_name \
           and self.model.organization and self.model.description 

