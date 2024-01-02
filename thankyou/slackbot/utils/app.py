import logging
from threading import Lock

from slack_bolt import App
from slack_sdk import WebClient

from thankyou.core.config import slack_bot_token, slack_signing_secret, slack_app_token
from thankyou.dao import dao
from thankyou.slackbot.utils.oauth import oauth_settings
from thankyou.slackbot.handlers.configuration import home_page_configuration_button_clicked_action_handler, \
    home_page_configuration_admin_slack_user_ids_value_changed_action_handler, \
    home_page_configuration_notification_slack_channel_value_changed_action_handler, \
    home_page_configuration_stats_time_period_value_changed_action_handler, \
    home_page_configuration_max_number_of_messages_per_week_value_changed_action_handler, \
    home_page_configuration_edit_company_value_clicked_action_handler, \
    home_page_configuration_add_new_company_value_clicked_action_handler, \
    home_page_configuration_enable_rich_text_in_thank_you_messages_value_changed_action_handler, \
    home_page_configuration_enable_company_values_value_changed_action_handler, \
    home_page_configuration_enable_leaderboard_value_changed_action_handler, \
    home_page_configuration_max_number_of_thank_you_receivers_value_changed_action_handler, \
    home_page_configuration_enable_attaching_files_value_changed_action_handler, \
    home_page_configuration_max_attached_files_num_value_changed_action_handler, \
    home_page_configuration_enable_weekly_thank_you_limit_value_changed_action_handler, \
    home_page_configuration_enable_sharing_in_a_slack_channel_value_changed_action_handler
from thankyou.slackbot.handlers.homepage import app_home_opened_action_handler, \
    home_page_company_thank_you_button_clicked_action_handler, home_page_my_thank_you_button_clicked_action_handler, \
    home_page_say_thank_you_button_clicked_action_handler, home_page_show_leaders_button_clicked_action_handler
from thankyou.slackbot.handlers.shortcuts import say_thank_you_global_shortcut_action_handler, \
    say_thank_you_message_shortcut_action_handler
from thankyou.slackbot.handlers.slashcommands import merci_slash_command_action_handler
from thankyou.slackbot.handlers.thankyoudialog import thank_you_dialog_save_button_clicked_action_handler
from thankyou.slackbot.handlers.thankyoutypedialog import thank_you_type_dialog_save_button_clicked_action_handler, \
    thank_you_type_dialog_delete_value_button_clicked_action_handler, \
    thank_you_type_deletion_dialog_confirm_deletion_button_clicked_action_handler


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
for handler in logger.root.handlers:
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(filename)s %(funcName)s "
                                           "- %(thread)d - %(message)s"))
    handler.setLevel(logging.DEBUG)

__CREATE_APP_LOCK = Lock()
_IS_SOCKET_MODE = None

if oauth_settings and slack_signing_secret():
    _IS_SOCKET_MODE = False
    logger.info("Creating an HTTP app with OAuth")
    logger.info(f"Slack signing secret = '{str(slack_signing_secret())[0:3]}...'")
    app = App(
        signing_secret=slack_signing_secret(),
        oauth_settings=oauth_settings,
        logger=logger,
    )
    logger.info("Created")
elif slack_bot_token() and slack_app_token():
    _IS_SOCKET_MODE = True
    logger.info("Creating a socket mode app ...")
    with __CREATE_APP_LOCK:
        app = App(token=slack_bot_token(), logger=logger)
    logger.info("Created")
else:
    raise ValueError("Can not create a Slack application instance")


def is_socket_mode() -> bool:
    return _IS_SOCKET_MODE


@app.event("app_home_opened")
def _app_home_opened_action_handler(client: WebClient, event, logger):
    app_home_opened_action_handler(client, event, logger)


@app.action("home_page_company_thank_you_button_clicked")
def _home_page_company_thank_you_button_clicked_action_handler(ack, client, body, logger):
    ack()
    home_page_company_thank_you_button_clicked_action_handler(body, client, logger)


@app.action("home_page_show_leaders_button_clicked")
def _home_page_show_leaders_button_clicked_action_handler(ack, client, body, logger):
    ack()
    home_page_show_leaders_button_clicked_action_handler(body, client, logger)


@app.action("home_page_my_thank_you_button_clicked")
def _home_page_my_thank_you_button_clicked_action_handler(ack, client, body, logger):
    ack()
    home_page_my_thank_you_button_clicked_action_handler(body, client, logger)


@app.action("home_page_say_thank_you_button_clicked")
def _home_page_say_thank_you_button_clicked_action_handler(ack, client, body, logger):
    ack()
    home_page_say_thank_you_button_clicked_action_handler(body, client, logger)


@app.view("thank_you_dialog_save_button_clicked")
def _thank_you_dialog_save_button_clicked_action_handler(ack, client, body, logger):
    ack()
    thank_you_dialog_save_button_clicked_action_handler(body, client, logger)


@app.action("home_page_configuration_button_clicked")
def _home_page_configuration_button_clicked_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_button_clicked_action_handler(body, client, logger)


@app.action("home_page_configuration_admin_slack_user_ids_value_changed")
def _home_page_configuration_admin_slack_user_ids_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_admin_slack_user_ids_value_changed_action_handler(body, client, logger)


@app.action("home_page_configuration_enable_sharing_in_a_slack_channel_value_changed")
def _home_page_configuration_enable_sharing_in_a_slack_channel_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_enable_sharing_in_a_slack_channel_value_changed_action_handler(body, client, logger)


@app.action("home_page_configuration_notification_slack_channel_value_changed")
def _home_page_configuration_notification_slack_channel_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_notification_slack_channel_value_changed_action_handler(body, client, logger)


@app.action("home_page_configuration_enable_leaderboard_value_changed")
def _home_page_configuration_enable_leaderboard_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_enable_leaderboard_value_changed_action_handler(body, client, logger)


@app.action("home_page_configuration_stats_time_period_value_changed")
def _home_page_configuration_stats_time_period_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_stats_time_period_value_changed_action_handler(body, client, logger)


@app.action("home_page_configuration_max_number_of_thank_you_receivers_value_changed")
def _home_page_configuration_max_number_of_thank_you_receivers_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_max_number_of_thank_you_receivers_value_changed_action_handler(body, client, logger)


@app.action("home_page_configuration_enable_weekly_thank_you_limit_value_changed")
def _home_page_configuration_enable_weekly_thank_you_limit_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_enable_weekly_thank_you_limit_value_changed_action_handler(body, client, logger)


@app.action("home_page_configuration_max_number_of_messages_per_week_value_changed")
def _home_page_configuration_max_number_of_messages_per_week_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_max_number_of_messages_per_week_value_changed_action_handler(body, client, logger)


@app.action("home_page_configuration_edit_company_value_clicked")
def _home_page_configuration_edit_company_value_clicked_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_edit_company_value_clicked_action_handler(body, client, logger)


@app.action("home_page_configuration_add_new_company_value_clicked")
def _home_page_configuration_add_new_company_value_clicked_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_add_new_company_value_clicked_action_handler(body, client, logger)


@app.action("home_page_configuration_enable_rich_text_in_thank_you_messages_value_changed")
def _home_page_configuration_enable_rich_text_in_thank_you_messages_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_enable_rich_text_in_thank_you_messages_value_changed_action_handler(body, client, logger)


@app.action("home_page_configuration_enable_attaching_files_value_changed")
def _home_page_configuration_enable_attaching_files_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_enable_attaching_files_value_changed_action_handler(body, client, logger)


@app.action("home_page_configuration_max_attached_files_num_value_changed")
def _home_page_configuration_max_attached_files_num_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_max_attached_files_num_value_changed_action_handler(body, client, logger)


@app.action("home_page_configuration_enable_company_values_value_changed")
def _home_page_configuration_enable_company_values_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_enable_company_values_value_changed_action_handler(body, client, logger)


@app.view("thank_you_type_dialog_save_button_clicked")
def _thank_you_type_dialog_save_button_clicked_action_handler(ack, client, body, logger):
    ack()
    thank_you_type_dialog_save_button_clicked_action_handler(body, client, logger)


@app.action("thank_you_type_dialog_delete_value_button_clicked")
def _thank_you_type_dialog_delete_value_button_clicked_action_handler(ack, client, body, logger):
    ack()
    thank_you_type_dialog_delete_value_button_clicked_action_handler(body, client, logger)


@app.view("thank_you_type_deletion_dialog_confirm_deletion_button_clicked")
def _thank_you_type_deletion_dialog_confirm_deletion_button_clicked_action_handler(ack, client, body, logger):
    ack()
    thank_you_type_deletion_dialog_confirm_deletion_button_clicked_action_handler(body, client, logger)


@app.command("/merci")
def _merci_slash_command_action_handler(ack, client, body, logger):
    ack()
    merci_slash_command_action_handler(body, client, logger)


@app.shortcut("say_thank_you_global_shortcut")
def _say_thank_you_global_shortcut_action_handler(ack, client, body, logger):
    ack()
    say_thank_you_global_shortcut_action_handler(body, client, logger)


@app.shortcut("say_thank_you_message_shortcut")
def _say_thank_you_message_shortcut_action_handler(ack, client, body, logger):
    ack()
    say_thank_you_message_shortcut_action_handler(body, client, logger)


@app.error
def app_error_handler(error):
    dao.on_app_error(error)
