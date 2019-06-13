"""
Validating Dialog Example
=========================

This example shows how to dynamically validate a user's entries in a
TraitsUI dialog.  The example shows four things:

* how to enable/disable the 'OK' dialog button by tracking various error
  states and incrementing/decrementing the :py:attr:`ui.errors` count.

* how to perform additional checks when the user clicks the 'OK' dialog
  button, displaying an appropriate error message and returning control
  to the dialog on failure.

* setting an editor's 'invalid' state via a trait, which colors the
  textbox background to the error color.

* displaying feedback to the user in a number of additional ways, such as
  text explanations, alert icons, and icons with varying feedback levels.


"""

try:
    from zxcvbn import zxcvbn as test_strength
except ImportError:
    import warnings
    warnings.warn("zxcvbn package not installed, using dummy strength tester")

    def test_strength(password):
        """ A dummy password strength tester. """
        if password == "12345":
            return {
                'score': 0,
                'feedback': {
                    'suggestions': [
                        "12345? Amazing, I have the same combination on my luggage"
                    ]
                }
            }
        elif len(password) < 16:
            return {
                'score': len(password) // 4,
                'feedback': {
                    'suggestions': ["Type more characters"]
                }
            }
        else:
            return {
                'score': 4,
                'feedback': {'suggestions': []}
            }


from traits.etsconfig.api import ETSConfig
from pyface.api import ImageResource, MessageDialog
from traits.api import (
    Bool, HasStrictTraits, HTML, Instance, Password, Property, Range, Unicode,
    cached_property, on_trait_change
)
from traitsui.api import (
    Action, Handler, HGroup, Image, ImageEditor, Item, Menu, MenuBar,
    ModelView, OKCancelButtons, TextEditor, VGrid, VGroup, View
)

if ETSConfig.toolkit in {'qt4', 'qt'}:
    from traitsui.qt4.constants import WindowColor
    background_color = '#{0:x}{1:x}{2:x}'.format(*WindowColor.getRgb())
elif ETSConfig.toolkit == 'wx':
    from traitsui.wx.constants import WindowColor
    background_color = '#{0:x}{1:x}{2:x}'.format(*WindowColor.GetRGB())

from apptools.feedback.feedbackbot.model import FeedbackMessage
from apptools.feedback.feedbackbot.view import FeedbackController
from apptools.feedback.feedbackbot.utils import take_screenshot_qimg, \
    get_raw_qimg_data

#: A map of password strength values to icons.
strength_map = {
    i: ImageResource('squares_{}'.format(i + 1))
    for i in range(5)
}


#: Enough CSS so it looks like it at least belongs in this millenium
css = """
* {{
    background-color: {background_color};
}}
h1 {{
    font-family: "Open Sans", "Ariel", sans;
    font-size: 16px;
    font-weight: bold;
}}
p {{
    font-family: "Open Sans", "Ariel", sans;
    font-size: 12px;
}}
""".format(background_color=background_color)


#: A simple HTML template to give feedback.
explanation_template = """
<html>
<head>
<style media="screen" type="text/css">
{css}
</style>
</head>
<body>
<h1>Enter your username and password.</h1>

<p>{text}</p>
</body>
</html>
"""


class Credentials(HasStrictTraits):
    """ A class that holds a user's credentials.
    """

    #: The user's id.
    username = Unicode

    #: The user's password.
    password = Password

    def login(self):
        """ Dummy login method. """
        if self.password == '12345':
            return True, 'Amazing, I have the same combination on my luggage!'
        else:
            return False, 'Incorrect password or unknown user.'

    def create_account(self):
        """ Dummy account creation method. """
        if self.username in {'alice', 'bob'}:
            return False, "Username already exists."
        return True, 'Account created'


class NewAccountView(ModelView):
    """ Account creation dialog example.
    """

    #: Text explaining the dialog.
    explanation = Property(HTML, depends_on=['_password_suggestions',
                                             '+view_error'])

    #: The user's password entered a second time.
    password = Password

    #: The user's password strength.
    password_strength = Range(0, 4)

    #: Alert icon for username error.
    password_strength_icon = Property(Image, depends_on='password_strength')

    #: Alert icon for username error.
    username_icon = Image('@std:alert16')

    #: Alert icon for second password error.
    password_match_icon = Image('@std:alert16')

    # private traits ---------------------------------------------------------

    #: The suggestions for a stronger password.
    _password_suggestions = Unicode

    #: Whether there is anything entered for the username.
    _username_error = Bool(False, view_error=True)

    #: Whether the password is strong enough.
    _password_strength_error = Bool(False, view_error=True)

    #: Whether the two entered passwords match.
    _password_match_error = Bool(False, view_error=True)

    # ------------------------------------------------------------------------
    # Handler interface
    # ------------------------------------------------------------------------

    def init(self, info):
        """ Initialize the error state of the object. """
        obj = info.object
        model = info.model

        # check for initial error states
        obj._check_username(model.username)
        obj._check_password_strength(model.password)
        obj._check_password_match(model.password)

        super(NewAccountView, self).init(info)

    def close(self, info, is_ok):
        """ Handles the user attempting to close the dialog.

        If it is via the OK dialog button, try to create an account before
        closing. If this fails, display an error message and veto the close
        by returning false.
        """
        if is_ok:
            success, message = info.model.create_account()
            if not success:
                dlg = MessageDialog(
                    message="Cannot create account",
                    informative=message,
                    severity='error'
                )
                dlg.open()
                return False

        return True

    # UI change handlers -----------------------------------------------------

    def model_username_changed(self, ui_info):
        """ Set error condition if the model's username is empty. """
        if ui_info.initialized:
            ui_info.object._username_error = (ui_info.model.username == '')

    def model_password_changed(self, ui_info):
        """ Check the quality of the password that the user entered. """
        if ui_info.initialized:
            obj = ui_info.object
            password = ui_info.model.password

            obj._check_password_strength(password)
            obj._check_password_match(password)

    def object_password_changed(self, ui_info):
        """ Check if the re-enteredpassword matches the original. """
        if ui_info.initialized:
            obj = ui_info.object
            password = ui_info.model.password

            obj._check_password_match(password)

    # ------------------------------------------------------------------------
    # private interface
    # ------------------------------------------------------------------------

    def _check_username(self, username):
        """ Check whether the passwords match. """
        self._username_error = (username == '')

    def _check_password_strength(self, password):
        """ Check the strength of the password

        This sets the password strength, suggestions for making a better
        password and an error state if the password is not strong enough.
        """
        if password:
            password_check = test_strength(password)
            self.password_strength = password_check['score']
            feedback = password_check.get('feedback', {})
            if feedback.get('warnings'):
                warnings = '<em>{}</em> '.format(feedback['warnings'])
            else:
                warnings = ''
            suggestions = feedback.get('suggestions', [])
            self._password_suggestions = warnings + ' '.join(suggestions)
        else:
            self.password_strength = 0
            self._password_suggestions = 'The password cannot be empty.'

        self._password_strength_error = (self.password_strength < 3)

    def _check_password_match(self, password):
        """ Check whether the passwords match. """
        self._password_match_error = (not password or password != self.password)

    # Trait change handlers --------------------------------------------------

    @on_trait_change("+view_error")
    def _view_error_updated(self, new_error):
        """ One of the error traits changed: update the error count. """
        if self.info and self.info.ui:
            if new_error:
                self.info.ui.errors += 1
            else:
                self.info.ui.errors -= 1

    # Traits property handlers -----------------------------------------------

    @cached_property
    def _get_password_strength_icon(self):
        """ Get the icon for password strength. """
        return strength_map[self.password_strength]

    @cached_property
    def _get_explanation(self):
        """ Get the explanatory HTML. """
        text = ''
        if self._username_error:
            text += 'The username cannot be empty. '
        if self._password_match_error:
            text += 'The passwords must match. '
        if self._password_suggestions:
            text += self._password_suggestions
        if not text:
            text = ("The username is valid, the password is strong and both "
                    + "password fields match.")
        return explanation_template.format(css=css, text=text)

    # TraitsUI view ----------------------------------------------------------

    view = View(
        VGroup(
            Item('explanation',show_label=False),
            VGrid(
                Item(
                    'model.username',
                    tooltip='The username to use when logging in.',
                    editor=TextEditor(invalid='_username_error')
                ),
                Item(
                    'username_icon',
                    editor=ImageEditor(),
                    show_label=False,
                    visible_when='_username_error',
                    tooltip='User name must not be empty.',
                ),
                Item(
                    'model.password',
                    tooltip='The password to use when logging in.',
                    editor=TextEditor(
                        invalid='_password_strength_error',
                        password=True,
                    )
                ),
                Item(
                    'password_strength_icon',
                    editor=ImageEditor(),
                    show_label=False,
                ),
                Item(
                    'password',
                    label='Re-enter Password:',
                    tooltip='Enter the password a second time.',
                    editor=TextEditor(
                        invalid='_password_match_error',
                        password=True,
                    )
                ),
                Item(
                    'password_match_icon',
                    editor=ImageEditor(),
                    show_label=False,
                    visible_when='_password_match_error',
                    tooltip='Passwords must match.',
                ),
                columns=2,
                show_border=True,
            ),
        ),
        title='Create User Account',
        buttons=OKCancelButtons,
        width=480,
        height=280,
    )


class MainApp(HasStrictTraits):
    """ A dummy main app to show the demo. """

    #: Information about the example.
    information = HTML()

    #: Information about the example.
    credentials = Instance(Credentials, ())

    def _information_default(self):
        return """
        <html>
        <head>
        <style media="screen" type="text/css">
        {css}
        </style>
        </head>
        <body>
        <h1>Validating Dialog Example</h1>

        <p>This example shows how to dynamically validate a user's entries in a
        TraitsUI dialog.  The example shows four things:</p>

        <ul>
        <li><p>how to enable/disable the 'OK' dialog button by tracking various
        error states and incrementing/decrementing the <code>ui.errors</code>
        count.</p></li>

        <li><p>how to perform additional checks when the user clicks the 'OK'
        dialog button, displaying an appropriate error message and returning
        control to the dialog on failure.</p></li>

        <li><p>setting an editor's 'invalid' state via a trait, which colors the
        textbox background to the error color.</p></li>

        <li><p>displaying feedback to the user in a number of additional ways,
        such as text explanations, alert icons, and icons with varying
        feedback levels.</p></li>
        </ul>
        </body>
        """.format(css=css)


class MainAppHandler(Handler):
    """ A handler to invoke the dialog. """

    def create_account(self, ui_info):

        credentials = Credentials(username='alice')
        modelview = NewAccountView(model=credentials)
        success = modelview.edit_traits(kind='livemodal')
        print("Logged in:", success)
        print("Username:", credentials.username)
        print("Password:", credentials.password)

        if success:
            ui_info.object.credentials = credentials

    def create_feedback_dialog(self, ui_info):

        img_bytes, img_h, img_w = get_raw_qimg_data(
            take_screenshot_qimg(ui_info))

        msg = FeedbackMessage(img_bytes=img_bytes, img_h=img_h, 
            img_w=img_w, channels='#general')

        msg_controller = FeedbackController(model=msg)
        msg_controller.configure_traits()



#: A view for the main app which displays an explanation and the username.
app_view = View(
    Item('information', style='readonly', show_label=False),
    HGroup(
        Item('object.credentials.username', style='readonly')
    ),
    menubar=MenuBar(
        Menu(
            Action(name='Create Account', action='create_account'),
            name='File',
        ),
        Menu(
            Action(name='Feedback/Bugs', action='create_feedback_dialog'),
            name='Help',),
    ),
    buttons=[
        Action(name='Create Account', action='create_account'),
        'OK',
    ],
    width=480,
    height=320,
    resizable=True,
)

if __name__ == '__main__':
    app = MainApp()
    app.configure_traits(view=app_view, handler=MainAppHandler())
