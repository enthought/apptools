Model and GUI logic for a Feedback/Bugs dialog box. The comments in this
[example app](https://github.com/enthought/apptools/tree/master/examples/feedback)
demonstrate how the dialog box can be incorporated in any TraitsUI app.

### Requirements:
- python3
- numpy
- PIL 
- python-slackclient

### Slack setup

Create a Slack app and install it to the Slack workspace. Then, add a bot user
to the app (detailed instructions are provided
[here](https://api.slack.com/bot-users)).

#### Tokens, authentication, and security

Requests to the Slack API have to be authenticated with an authorization token.
A token for the bot-user will be created automatically when the bot is added to
the Slack app. This token must be provided to the model class when an instance
is created.

The bearer of a bot token has a pretty broad set of permissions. For instance,
they can upload files to a channel, lookup a user with an email address, and
even get the entire conversation history of a channel (see this
[link](https://api.slack.com/bot-users#methods) for a full list of functions
accessible with a bot token). Needless to say, tokens must be secured and never
revealed publicly. The responsibility of transmitting tokens securely lies with the
developer of the app incorporating this dialog box. Refer to the [Slack API
documentation](https://api.slack.com/docs/oauth-safety)
for security best-practices.
