from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler

from thankyou.slackbot.utils.app import app


def create_flask_app(slack_app_):
    flask_app = Flask(__name__)
    slack_handler = SlackRequestHandler(slack_app_)

    @flask_app.route("/slack/events", methods=["POST"])
    def slack_events():
        return slack_handler.handle(request)

    @flask_app.route("/slack/install", methods=["GET"])
    def install():
        return slack_handler.handle(request)

    @flask_app.route("/slack/oauth_redirect", methods=["GET"])
    def oauth_redirect():
        return slack_handler.handle(request)

    return flask_app


def slack_app():
    return create_flask_app(app)
