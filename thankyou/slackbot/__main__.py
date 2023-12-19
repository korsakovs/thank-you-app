import logging

from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

from thankyou.core.config import slack_app_token
from thankyou.slackbot.app import app
from thankyou.slackbot.handlers.configuration import home_page_configuration_button_clicked_action_handler
from thankyou.slackbot.handlers.homepage import app_home_opened_action_handler, \
    home_page_company_thank_you_button_clicked_action_handler, home_page_my_thank_you_button_clicked_action_handler, \
    home_page_say_thank_you_button_clicked_action_handler, home_page_show_leaders_button_clicked_action_handler
from thankyou.slackbot.handlers.thankyoudialog import thank_you_dialog_save_button_clicked_action_handler


@app.event("app_home_opened")
def _app_home_opened_action_handler(client: WebClient, event, logger):
    app_home_opened_action_handler(client, event, logger)


@app.action("home_page_company_thank_you_button_clicked")
def _home_page_company_thank_you_button_clicked_action_handler(ack, body, logger):
    ack()
    home_page_company_thank_you_button_clicked_action_handler(body, logger)


@app.action("home_page_show_leaders_button_clicked")
def _home_page_show_leaders_button_clicked_action_handler(ack, body, logger):
    ack()
    home_page_show_leaders_button_clicked_action_handler(body, logger)


@app.action("home_page_my_thank_you_button_clicked")
def _home_page_my_thank_you_button_clicked_action_handler(ack, body, logger):
    ack()
    home_page_my_thank_you_button_clicked_action_handler(body, logger)


@app.action("home_page_say_thank_you_button_clicked")
def _home_page_say_thank_you_button_clicked_action_handler(ack, body, logger):
    ack()
    home_page_say_thank_you_button_clicked_action_handler(body, logger)


@app.view("thank_you_dialog_save_button_clicked")
def _thank_you_dialog_save_button_clicked_action_handler(ack, body, logger):
    ack()
    thank_you_dialog_save_button_clicked_action_handler(body, logger)


@app.action("home_page_configuration_button_clicked")
def _home_page_configuration_button_clicked_action_handler(ack, body, logger):
    ack()
    home_page_configuration_button_clicked_action_handler(body, logger)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    handler = SocketModeHandler(app, slack_app_token())
    handler.start()
