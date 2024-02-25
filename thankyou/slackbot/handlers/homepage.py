from datetime import datetime, timedelta
from typing import Optional

from cachetools import cached, TTLCache
from slack_sdk import WebClient

from thankyou.dao import dao
from thankyou.slackbot.handlers.common import get_sender_and_receiver_leaders
from thankyou.slackbot.utils.company import get_or_create_company_by_event, get_or_create_company_by_slack_team_id, \
    get_or_create_company_by_body
from thankyou.slackbot.utils.employee import get_or_create_employee_by_slack_user_id
from thankyou.slackbot.views.help import home_page_help_view
from thankyou.slackbot.views.homepage import home_page_company_thank_yous_view, home_page_my_thank_yous_view
from thankyou.slackbot.views.thankyoudialog import thank_you_dialog_view


@cached(cache=TTLCache(maxsize=1024, ttl=60))
def messages_sent_num(company_uuid: str, interval: timedelta = timedelta(days=30), private: Optional[bool] = False):
    return dao.read_thank_you_messages_num(company_uuid=company_uuid, created_after=datetime.utcnow() - interval,
                                           private=private)


def app_home_opened_action_handler(client: WebClient, event, logger):
    try:
        company = get_or_create_company_by_event(event)
    except Exception:
        company = get_or_create_company_by_slack_team_id(client.default_params["team_id"])

    user_id = event["user"]
    employee = get_or_create_employee_by_slack_user_id(company_uuid=company.uuid, slack_user_id=user_id)

    messages = dao.read_thank_you_messages(company_uuid=company.uuid, last_n=20, private=False)

    slack_channel_with_all_messages = None
    if company.enable_sharing_in_a_slack_channel and company.share_messages_in_slack_channel:
        slack_channel_with_all_messages = company.share_messages_in_slack_channel

    hidden_messages_num = max(0, messages_sent_num(company_uuid=company.uuid, private=False) - len(messages))

    view = home_page_company_thank_yous_view(
        thank_you_messages=messages,
        current_user_slack_id=user_id,
        enable_leaderboard=company.enable_leaderboard,
        slack_channel_with_all_messages=slack_channel_with_all_messages,
        hidden_messages_num=hidden_messages_num,
        show_welcome_message=not employee.closed_welcome_message
    )

    client.views_publish(
        user_id=user_id,
        view=view
    )


def home_page_company_thank_you_button_clicked_action_handler(body, client, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)
    employee = get_or_create_employee_by_slack_user_id(company_uuid=company.uuid, slack_user_id=user_id)

    messages = dao.read_thank_you_messages(company_uuid=company.uuid, last_n=20, private=False)

    slack_channel_with_all_messages = None
    if company.enable_sharing_in_a_slack_channel and company.share_messages_in_slack_channel:
        slack_channel_with_all_messages = company.share_messages_in_slack_channel

    hidden_messages_num = max(0, messages_sent_num(company_uuid=company.uuid, private=False) - len(messages))

    client.views_publish(
        user_id=user_id,
        view=home_page_company_thank_yous_view(
            thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, last_n=20, private=False),
            current_user_slack_id=user_id,
            enable_leaderboard=company.enable_leaderboard,
            slack_channel_with_all_messages=slack_channel_with_all_messages,
            hidden_messages_num=hidden_messages_num,
            show_welcome_message=not employee.closed_welcome_message
        )
    )


def home_page_show_leaders_button_clicked_action_handler(body, client, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)
    employee = get_or_create_employee_by_slack_user_id(company_uuid=company.uuid, slack_user_id=user_id)

    senders_receivers_stats = get_sender_and_receiver_leaders(
        company_uuid=company.uuid,
        leaderboard_time_settings=company.leaderbord_time_settings,
        group_by_company_values=company.enable_company_values,
        include_private=company.enable_private_message_counting_in_leaderboard
    )

    client.views_publish(
        user_id=user_id,
        view=home_page_company_thank_yous_view(
            thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, last_n=20, private=False),
            current_user_slack_id=user_id,
            sender_leaders=senders_receivers_stats.sender_leaders,
            receiver_leaders=senders_receivers_stats.receiver_leaders,
            leaders_stats_from_date=senders_receivers_stats.leaders_stats_from_datetime.date(),
            leaders_stats_until_date=senders_receivers_stats.leaders_stats_until_datetime.date(),
            enable_leaderboard=company.enable_leaderboard,
            show_welcome_message=not employee.closed_welcome_message
        )
    )


def home_page_my_thank_you_button_clicked_action_handler(body, client, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    client.views_publish(
        user_id=user_id,
        view=home_page_my_thank_yous_view(
            thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, author_slack_user_id=user_id,
                                                           last_n=20),
            current_user_slack_id=user_id
        )
    )


def home_page_say_thank_you_button_clicked_action_handler(body, client, logger):
    company = get_or_create_company_by_body(body)
    user_id = body["user"]["id"]

    beginning_of_the_week = (datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                             - timedelta(days=datetime.utcnow().weekday()))
    end_of_the_week = beginning_of_the_week + timedelta(days=7)
    sent_messages_num = len(dao.read_thank_you_messages(
        company_uuid=company.uuid,
        author_slack_user_id=user_id,
        created_after=beginning_of_the_week,
        created_before=end_of_the_week
    ))

    if company.enable_weekly_thank_you_limit:
        num_of_messages_a_user_can_send = max(0, company.weekly_thank_you_limit - sent_messages_num)
    else:
        num_of_messages_a_user_can_send = None

    try:
        client.views_open(
            trigger_id=body["trigger_id"],
            view=thank_you_dialog_view(
                thank_you_types=dao.read_thank_you_types(company_uuid=company.uuid),
                enable_rich_text=company.enable_rich_text_in_thank_you_messages,
                enable_company_values=company.enable_company_values,
                max_receivers_num=company.receivers_number_limit,
                enable_attaching_files=company.enable_attaching_files,
                max_attached_files_num=company.max_attached_files_num,
                num_of_messages_a_user_can_send=num_of_messages_a_user_can_send,
                display_private_message_option=company.enable_private_messages,
            ),
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


def home_page_hide_welcome_message_button_clicked_action_handler(body, client, logger):
    company = get_or_create_company_by_body(body)
    employee = get_or_create_employee_by_slack_user_id(company_uuid=company.uuid, slack_user_id=body["user"]["id"])

    messages = dao.read_thank_you_messages(company_uuid=company.uuid, last_n=20, private=False)
    hidden_messages_num = max(0, messages_sent_num(company_uuid=company.uuid, private=False) - len(messages))

    if not employee.closed_welcome_message:
        employee.closed_welcome_message = True

    client.views_publish(
        user_id=employee.slack_user_id,
        view=home_page_company_thank_yous_view(
            thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, last_n=20, private=False),
            current_user_slack_id=employee.slack_user_id,
            enable_leaderboard=company.enable_leaderboard,
            slack_channel_with_all_messages=company.share_messages_in_slack_channel,
            hidden_messages_num=hidden_messages_num,
            show_welcome_message=not employee.closed_welcome_message
        )
    )


def home_page_help_button_clicked_action_handler(body, client, logger):
    client.views_publish(
        user_id=body["user"]["id"],
        view=home_page_help_view()
    )
