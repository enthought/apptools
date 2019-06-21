"""
Feedback Dialog Example
=========================

This example shows how the feedback dialog can be included in an application.
The client-user interface is described in the
FeedbackExampleApp.client_user_explanation attribute. All other comments are
aimed at the developer interested in including the feedback dialog in their
app (see especially `feedback_example_view` and the `FeedbackExampleHandler`
class).

"""

import os

from traits.api import HasTraits, Str
from traitsui.api import (
    Item, Menu, MenuBar, OKCancelButtons, View, Action, Handler
)

from apptools.feedback.feedbackbot.utils import initiate_feedback_dialog_


class FeedbackExampleApp(HasTraits):
    """ A simple model to demonstrate the feedback dialog."""

    #: This attribute explains the client-user interface.
    client_user_explanation = Str

    def _client_user_explanation_default(self):

        return """
        This app demonstrates how to use the feedback dialog.

        To begin, click on Feedback/Bugs in the Help menu. This will
        automatically take a screenshot of this app, and launch the feedback
        dialog box. You should be able to see a preview of the
        screenshot in the dialog box.

        Next, enter your details, and a description of the problem. All fields
        are mandatory, and you can't send the message till you type something
        in each field. When you're done, click on the Send button. The dialog
        is pre-configured by our developers to ensure it reaches
        the right team.

        The dialog will notify you of successful delivery of the message, or if
        any problems occured."""


# View for the example app. The feedbackbot module provides a helper function
# `initiate_feedback_dialog_` that launches the feedback dialog box. To include
# the feedback dialog box in the app, simply call this function from an
# appropriate place. In this example, we call it from the Feedback/Bugs menu
# item in the Help menu.
feedback_example_view = View(
    Item('client_user_explanation', style='readonly', show_label=False),
    menubar=MenuBar(
        Menu(
            Action(name='Feedback/Bugs', action='initiate_feedback_dialog'),
            name='Help'),
    ),
    buttons=OKCancelButtons,
    width=480,
    height=320,
    title='Example App',
    resizable=True,
)


class FeedbackExampleHandler(Handler):
    """ Simple handler for the FeedbackExampleApp. """

    def initiate_feedback_dialog(self, ui_info):
        """ Initiates the feedback dialog. """

        # As mentioned earlier, the feedback dialog can be initiated by
        # invoking the `initiate_feedback_dialog_` function. The first argument
        # to this function is the control object whose screenshot will be
        # grabbed. The second argument is the OAuth token for the bot (see
        # the feedbackbot README for an explanation). In practice, you (the
        # user-developer) will have to decide on an appropriate way to
        # pass around the token (again, see the README for a discussion on what
        # could go wrong if the token gets leaked.). The third argument is the
        # channel where you'd like messages from this app to go. The value for
        # this argument must start with '#'.
        initiate_feedback_dialog_(ui_info.ui.control,
                                  os.environ['FEEDBACKBOT_OAUTH_TOKEN'],
                                  '#general')


if __name__ == '__main__':

    app = FeedbackExampleApp()

    app.configure_traits(view=feedback_example_view,
                         handler=FeedbackExampleHandler())
