from flask import Flask, request, Response
from slack_bolt.adapter.flask import SlackRequestHandler

from thankyou.dao import dao
from thankyou.slackbot.utils.app import app
from thankyou.slackbot.utils.pages.installbutton import build_default_install_page_html
from thankyou.slackbot.utils.pages.privacy import privacy_page_html
from thankyou.slackbot.utils.pages.termsofservice import terms_of_service
from thankyou.utils.flask import flask_scoped_session


def create_flask_app(slack_app_):
    flask_app = Flask(__name__)
    slack_handler = SlackRequestHandler(slack_app_)

    dao.set_scoped_session(flask_scoped_session(dao.session_maker, flask_app))

    @flask_app.route("/slack/events", methods=["POST"])
    def slack_events():
        return slack_handler.handle(request)

    @flask_app.route("/slack/install_button", methods=["GET"])
    def install_button():
        return Response(
            status=200,
            response=build_default_install_page_html("https://merci.emgbook.com/slack/install")
        )

    @flask_app.route("/slack/install", methods=["GET"])
    def install():
        return slack_handler.handle(request)

    @flask_app.route("/slack/oauth_redirect", methods=["GET"])
    def oauth_redirect():
        return slack_handler.handle(request)

    @flask_app.route("/slack/privacy", methods=["GET"])
    def privacy():
        return Response(
            status=200,
            response=privacy_page_html
        )

    @flask_app.route("/slack/tos", methods=["GET"])
    def tos():
        return Response(
            status=200,
            response=terms_of_service
        )

    return flask_app


def slack_app():
    return create_flask_app(app)
