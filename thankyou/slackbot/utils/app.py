import logging

from slack_bolt import App

from thankyou.core.config import slack_bot_token, slack_signing_secret, slack_app_token
from thankyou.slackbot.utils.oauth import oauth_settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
for handler in logger.root.handlers:
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(filename)s %(funcName)s "
                                           "- %(thread)d - %(message)s"))

_IS_SOCKET_MODE = None

if oauth_settings and slack_signing_secret():
    _IS_SOCKET_MODE = False
    app = App(
        signing_secret=slack_signing_secret(),
        oauth_settings=oauth_settings,
        logger=logger
    )
elif slack_bot_token() and slack_app_token():
    _IS_SOCKET_MODE = True
    app = App(token=slack_bot_token(), logger=logger)
else:
    raise ValueError("Can not create a Slack application instance")


def is_socket_mode() -> bool:
    return _IS_SOCKET_MODE
