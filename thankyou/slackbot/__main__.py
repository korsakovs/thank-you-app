from prometheus_client import start_http_server
from slack_bolt.adapter.socket_mode import SocketModeHandler

from thankyou.core.config import slack_app_token
from thankyou.slackbot.utils.app import app, is_socket_mode


if __name__ == "__main__":
    start_http_server(8010)

    if is_socket_mode():
        handler = SocketModeHandler(app, slack_app_token())
        handler.start()
    else:
        app.start(port=3000)
