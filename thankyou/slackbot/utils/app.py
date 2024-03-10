import logging
from enum import Enum
from functools import wraps
from threading import Lock
from timeit import default_timer as timer
from typing import Callable

from prometheus_client import Histogram, Counter as PrometheusCounter
from slack_bolt import App
from slack_sdk import WebClient

from thankyou.core.config import slack_bot_token, slack_signing_secret, slack_app_token
from thankyou.slackbot.handlers.thankyoumessage import thank_you_message_say_thanks_button_clicked_handler, \
    thanks_back_dialog_send_button_clicked_handler, thank_you_message_overflow_menu_clicked_handler, \
    thank_you_deletion_dialog_delete_button_clicked
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
    home_page_configuration_enable_sharing_in_a_slack_channel_value_changed_action_handler, \
    home_page_configuration_enable_private_messages_value_changed_action_handler, \
    handle_home_page_configuration_enable_private_message_counting_in_leaderboard_value_changed_action_handler
from thankyou.slackbot.handlers.homepage import app_home_opened_action_handler, \
    home_page_company_thank_you_button_clicked_action_handler, home_page_my_thank_you_button_clicked_action_handler, \
    home_page_say_thank_you_button_clicked_action_handler, home_page_show_leaders_button_clicked_action_handler, \
    home_page_hide_welcome_message_button_clicked_action_handler, home_page_help_button_clicked_action_handler
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


slack_handler_metric = Histogram(
    name='slack_handler_metric_histogram',
    documentation='Time spent processing request',
    labelnames=["merci_handler", "merci_handler_type"],
)

events_counter = PrometheusCounter(
    name='slack_handler_number_of_events',
    documentation='The total number of requests received',
)


errors_counter = PrometheusCounter(
    name='slack_handler_number_of_errors',
    documentation='The total number of errors happened while processing requests',
)


class EventType(Enum):
    Event = "event"
    Action = "action"
    View = "view"
    Command = "command"
    Shortcut = "shortcut"


def app_event(event_type: EventType, name: str):
    def decorator(func: Callable):
        metric_wrapper = slack_handler_metric.labels(func.__name__, event_type.value)

        if event_type == EventType.Event:
            app_wrapper = app.event
        elif event_type == EventType.Action:
            app_wrapper = app.action
        elif event_type == EventType.View:
            app_wrapper = app.view
        elif event_type == EventType.Command:
            app_wrapper = app.command
        elif event_type == EventType.Shortcut:
            app_wrapper = app.shortcut
        else:
            raise ValueError(f"Unknown EventType: {event_type}")

        @app_wrapper(name)
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = timer()
            try:
                return func(*args, **kwargs)
            except Exception:
                errors_counter.inc(1)
                raise
            finally:
                # logger.info(f"Sending metrics for {func.__name__}")
                events_counter.inc(1)
                metric_wrapper.observe(timer() - start)

        return wrapper
    return decorator


@app_event(EventType.Event, "app_home_opened")
def _app_home_opened_action_handler(client: WebClient, event, logger):
    app_home_opened_action_handler(client, event, logger)


@app_event(EventType.Action, "home_page_company_thank_you_button_clicked")
def _home_page_company_thank_you_button_clicked_action_handler(ack, client, body, logger):
    ack()
    home_page_company_thank_you_button_clicked_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_show_leaders_button_clicked")
def _home_page_show_leaders_button_clicked_action_handler(ack, client, body, logger):
    ack()
    home_page_show_leaders_button_clicked_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_my_thank_you_button_clicked")
def _home_page_my_thank_you_button_clicked_action_handler(ack, client, body, logger):
    ack()
    home_page_my_thank_you_button_clicked_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_say_thank_you_button_clicked")
def _home_page_say_thank_you_button_clicked_action_handler(ack, client, body, logger):
    ack()
    home_page_say_thank_you_button_clicked_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_hide_welcome_message_button_clicked")
def _home_page_hide_welcome_message_button_clicked_action_handler(ack, client, body, logger):
    ack()
    home_page_hide_welcome_message_button_clicked_action_handler(body, client, logger)


@app_event(EventType.Action, "thank_you_dialog_send_privately_action")
def _thank_you_dialog_send_privately_action_handler(ack):
    ack()


@app_event(EventType.View, "thank_you_dialog_save_button_clicked")
def _thank_you_dialog_save_button_clicked_action_handler(ack, client, body, logger):
    ack()
    thank_you_dialog_save_button_clicked_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_help_button_clicked")
def _home_page_help_button_clicked_action_handler(ack, client, body, logger):
    ack()
    home_page_help_button_clicked_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_configuration_button_clicked")
def _home_page_configuration_button_clicked_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_button_clicked_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_configuration_admin_slack_user_ids_value_changed")
def _home_page_configuration_admin_slack_user_ids_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_admin_slack_user_ids_value_changed_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_configuration_enable_sharing_in_a_slack_channel_value_changed")
def _home_page_configuration_enable_sharing_in_a_slack_channel_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_enable_sharing_in_a_slack_channel_value_changed_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_configuration_notification_slack_channel_value_changed")
def _home_page_configuration_notification_slack_channel_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_notification_slack_channel_value_changed_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_configuration_enable_private_messages_value_changed")
def _home_page_configuration_enable_private_messages_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_enable_private_messages_value_changed_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_configuration_enable_leaderboard_value_changed")
def _home_page_configuration_enable_leaderboard_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_enable_leaderboard_value_changed_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_configuration_stats_time_period_value_changed")
def _home_page_configuration_stats_time_period_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_stats_time_period_value_changed_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_configuration_enable_private_message_counting_in_leaderboard_value_changed")
def _handle_home_page_configuration_enable_private_message_counting_in_leaderboard_value_changed_action_handler(ack, client, body, logger):
    ack()
    handle_home_page_configuration_enable_private_message_counting_in_leaderboard_value_changed_action_handler(client, body, logger)


@app_event(EventType.Action, "home_page_configuration_max_number_of_thank_you_receivers_value_changed")
def _home_page_configuration_max_number_of_thank_you_receivers_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_max_number_of_thank_you_receivers_value_changed_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_configuration_enable_weekly_thank_you_limit_value_changed")
def _home_page_configuration_enable_weekly_thank_you_limit_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_enable_weekly_thank_you_limit_value_changed_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_configuration_max_number_of_messages_per_week_value_changed")
def _home_page_configuration_max_number_of_messages_per_week_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_max_number_of_messages_per_week_value_changed_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_configuration_edit_company_value_clicked")
def _home_page_configuration_edit_company_value_clicked_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_edit_company_value_clicked_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_configuration_add_new_company_value_clicked")
def _home_page_configuration_add_new_company_value_clicked_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_add_new_company_value_clicked_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_configuration_enable_rich_text_in_thank_you_messages_value_changed")
def _home_page_configuration_enable_rich_text_in_thank_you_messages_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_enable_rich_text_in_thank_you_messages_value_changed_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_configuration_enable_attaching_files_value_changed")
def _home_page_configuration_enable_attaching_files_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_enable_attaching_files_value_changed_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_configuration_max_attached_files_num_value_changed")
def _home_page_configuration_max_attached_files_num_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_max_attached_files_num_value_changed_action_handler(body, client, logger)


@app_event(EventType.Action, "home_page_configuration_enable_company_values_value_changed")
def _home_page_configuration_enable_company_values_value_changed_action_handler(ack, client, body, logger):
    ack()
    home_page_configuration_enable_company_values_value_changed_action_handler(body, client, logger)


@app_event(EventType.View, "thank_you_type_dialog_save_button_clicked")
def _thank_you_type_dialog_save_button_clicked_action_handler(ack, client, body, logger):
    ack()
    thank_you_type_dialog_save_button_clicked_action_handler(body, client, logger)


@app_event(EventType.Action, "thank_you_type_dialog_delete_value_button_clicked")
def _thank_you_type_dialog_delete_value_button_clicked_action_handler(ack, client, body, logger):
    ack()
    thank_you_type_dialog_delete_value_button_clicked_action_handler(body, client, logger)


@app_event(EventType.View, "thank_you_type_deletion_dialog_confirm_deletion_button_clicked")
def _thank_you_type_deletion_dialog_confirm_deletion_button_clicked_action_handler(ack, client, body, logger):
    ack()
    thank_you_type_deletion_dialog_confirm_deletion_button_clicked_action_handler(body, client, logger)


@app_event(EventType.Action, "thank_you_message_say_thanks_button_clicked")
def _thank_you_message_say_thanks_button_clicked_handler(ack, client, body, logger):
    ack()
    thank_you_message_say_thanks_button_clicked_handler(body, client, logger)


@app_event(EventType.Action, "thank_you_message_overflow_menu_clicked")
def _thank_you_message_overflow_menu_clicked_handler(ack, client, body, logger):
    ack()
    thank_you_message_overflow_menu_clicked_handler(client, body, logger)


@app_event(EventType.View, "thank_you_deletion_dialog_delete_button_clicked")
def _thank_you_deletion_dialog_delete_button_clicked(ack, client, body, logger):
    ack()
    thank_you_deletion_dialog_delete_button_clicked(client, body, logger)


@app_event(EventType.View, "thanks_back_dialog_send_button_clicked")
def _thanks_back_dialog_send_button_clicked_handler(ack, client, body, logger):
    ack()
    thanks_back_dialog_send_button_clicked_handler(body, client, logger)


@app_event(EventType.Command, "/merci")
def _merci_slash_command_action_handler(ack, client, body, logger):
    ack()
    merci_slash_command_action_handler(body, client, logger)


@app_event(EventType.Command, "/thanks")
def _merci_slash_command_action_handler(ack, client, body, logger):
    ack()
    merci_slash_command_action_handler(body, client, logger)


@app_event(EventType.Command, "/merci_dev")
def _merci_slash_command_action_handler(ack, client, body, logger):
    ack()
    merci_slash_command_action_handler(body, client, logger)


@app_event(EventType.Shortcut, "say_thank_you_global_shortcut")
def _say_thank_you_global_shortcut_action_handler(ack, client, body, logger):
    ack()
    say_thank_you_global_shortcut_action_handler(body, client, logger)


@app_event(EventType.Shortcut, "say_thank_you_message_shortcut")
def _say_thank_you_message_shortcut_action_handler(ack, client, body, logger):
    ack()
    say_thank_you_message_shortcut_action_handler(body, client, logger)
