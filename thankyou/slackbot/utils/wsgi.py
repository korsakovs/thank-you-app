import logging
import threading

import greenlet
from flask import Flask, request, Response
from slack_bolt.adapter.flask import SlackRequestHandler
from sqlalchemy.orm import scoped_session

from thankyou.dao import dao
from thankyou.slackbot.utils.app import app
from thankyou.slackbot.utils.pages.installbutton import build_default_install_page_html
from thankyou.slackbot.utils.pages.privacy import privacy_page_html
from thankyou.slackbot.utils.pages.termsofservice import terms_of_service


logging.basicConfig(level=logging.DEBUG)


class flask_scoped_session(scoped_session):
    """A :class:`~sqlalchemy.orm.scoping.scoped_session` whose scope is set to
    the Flask application context.
    """
    def __init__(self, session_factory, flask_app: Flask = None):
        def scope_func():
            try:
                return greenlet.getcurrent()
            except Exception as e:
                logging.debug(f"Can not retrieve greenlet.getcurrent: {e}")
                try:
                    return threading.get_ident()
                except Exception as e:
                    logging.debug(f"Can not retrieve threading.get_ident: {e}")
                    return "default"

        super(flask_scoped_session, self).__init__(session_factory, scopefunc=scope_func)

        if flask_app is not None:
            flask_app.scoped_session = self

            @flask_app.teardown_appcontext
            def remove_scoped_session(*_, **__):
                flask_app.scoped_session.remove()


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
