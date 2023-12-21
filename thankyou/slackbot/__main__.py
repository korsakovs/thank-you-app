import logging

from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

from thankyou.core.config import slack_app_token
from thankyou.slackbot.app import app
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
    home_page_configuration_max_attached_files_num_value_changed_action_handler
from thankyou.slackbot.handlers.homepage import app_home_opened_action_handler, \
    home_page_company_thank_you_button_clicked_action_handler, home_page_my_thank_you_button_clicked_action_handler, \
    home_page_say_thank_you_button_clicked_action_handler, home_page_show_leaders_button_clicked_action_handler
from thankyou.slackbot.handlers.thankyoudialog import thank_you_dialog_save_button_clicked_action_handler
from thankyou.slackbot.handlers.thankyoutypedialog import thank_you_type_dialog_save_button_clicked_action_handler, \
    thank_you_type_dialog_delete_value_button_clicked_action_handler, \
    thank_you_type_deletion_dialog_confirm_deletion_button_clicked_action_handler


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


@app.action("home_page_configuration_admin_slack_user_ids_value_changed")
def _home_page_configuration_admin_slack_user_ids_value_changed_action_handler(ack, body, logger):
    ack()
    home_page_configuration_admin_slack_user_ids_value_changed_action_handler(body, logger)


@app.action("home_page_configuration_notification_slack_channel_value_changed")
def _home_page_configuration_notification_slack_channel_value_changed_action_handler(ack, body, logger):
    ack()
    home_page_configuration_notification_slack_channel_value_changed_action_handler(body, logger)


@app.action("home_page_configuration_enable_leaderboard_value_changed")
def _home_page_configuration_enable_leaderboard_value_changed_action_handler(ack, body, logger):
    ack()
    home_page_configuration_enable_leaderboard_value_changed_action_handler(body, logger)


@app.action("home_page_configuration_stats_time_period_value_changed")
def _home_page_configuration_stats_time_period_value_changed_action_handler(ack, body, logger):
    ack()
    home_page_configuration_stats_time_period_value_changed_action_handler(body, logger)


@app.action("home_page_configuration_max_number_of_thank_you_receivers_value_changed")
def _home_page_configuration_max_number_of_thank_you_receivers_value_changed_action_handler(ack, body, logger):
    ack()
    home_page_configuration_max_number_of_thank_you_receivers_value_changed_action_handler(body, logger)


@app.action("home_page_configuration_max_number_of_messages_per_week_value_changed")
def _home_page_configuration_max_number_of_messages_per_week_value_changed_action_handler(ack, body, logger):
    ack()
    home_page_configuration_max_number_of_messages_per_week_value_changed_action_handler(body, logger)


@app.action("home_page_configuration_edit_company_value_clicked")
def _home_page_configuration_edit_company_value_clicked_action_handler(ack, body, logger):
    ack()
    home_page_configuration_edit_company_value_clicked_action_handler(body, logger)


@app.action("home_page_configuration_add_new_company_value_clicked")
def _home_page_configuration_add_new_company_value_clicked_action_handler(ack, body, logger):
    ack()
    home_page_configuration_add_new_company_value_clicked_action_handler(body, logger)


@app.action("home_page_configuration_enable_rich_text_in_thank_you_messages_value_changed")
def _home_page_configuration_enable_rich_text_in_thank_you_messages_value_changed_action_handler(ack, body, logger):
    ack()
    home_page_configuration_enable_rich_text_in_thank_you_messages_value_changed_action_handler(body, logger)


@app.action("home_page_configuration_enable_attaching_files_value_changed")
def _home_page_configuration_enable_attaching_files_value_changed_action_handler(ack, body, logger):
    ack()
    home_page_configuration_enable_attaching_files_value_changed_action_handler(body, logger)


@app.action("home_page_configuration_max_attached_files_num_value_changed")
def _home_page_configuration_max_attached_files_num_value_changed_action_handler(ack, body, logger):
    ack()
    home_page_configuration_max_attached_files_num_value_changed_action_handler(body, logger)


@app.action("home_page_configuration_enable_company_values_value_changed")
def _home_page_configuration_enable_company_values_value_changed_action_handler(ack, body, logger):
    ack()
    home_page_configuration_enable_company_values_value_changed_action_handler(body, logger)


@app.view("thank_you_type_dialog_save_button_clicked")
def _thank_you_type_dialog_save_button_clicked_action_handler(ack, body, logger):
    ack()
    thank_you_type_dialog_save_button_clicked_action_handler(body, logger)


@app.action("thank_you_type_dialog_delete_value_button_clicked")
def _thank_you_type_dialog_delete_value_button_clicked_action_handler(ack, body, logger):
    ack()
    thank_you_type_dialog_delete_value_button_clicked_action_handler(body, logger)


@app.view("thank_you_type_deletion_dialog_confirm_deletion_button_clicked")
def _thank_you_type_deletion_dialog_confirm_deletion_button_clicked_action_handler(ack, body, logger):
    ack()
    thank_you_type_deletion_dialog_confirm_deletion_button_clicked_action_handler(body, logger)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    handler = SocketModeHandler(app, slack_app_token())
    handler.start()
