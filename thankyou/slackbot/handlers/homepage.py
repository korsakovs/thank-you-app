from datetime import datetime, timedelta

from slack_sdk import WebClient

from thankyou.dao import dao
from thankyou.slackbot.app import app
from thankyou.slackbot.handlers.common import get_sender_and_receiver_leaders
from thankyou.slackbot.utils.company import get_or_create_company_by_event, get_or_create_company_by_slack_team_id, \
    get_or_create_company_by_body
from thankyou.slackbot.views.homepage import home_page_company_thank_yous_view, home_page_my_thank_yous_view
from thankyou.slackbot.views.thankyoudialog import thank_you_dialog_view


def app_home_opened_action_handler(client: WebClient, event, logger):
    try:
        company = get_or_create_company_by_event(event)
    except Exception:
        company = get_or_create_company_by_slack_team_id(client.default_params["team_id"])

    user_id = event["user"]

    view = home_page_company_thank_yous_view(
        thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, last_n=20),
        current_user_slack_id=user_id,
        enable_leaderboard=company.enable_leaderboard,
    )

    client.views_publish(
        user_id=user_id,
        view=view
    )


def home_page_company_thank_you_button_clicked_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    app.client.views_publish(
        user_id=user_id,
        view=home_page_company_thank_yous_view(
            thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, last_n=20),
            current_user_slack_id=user_id,
            enable_leaderboard=company.enable_leaderboard,
        )
    )


def home_page_show_leaders_button_clicked_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    senders_receivers_stats = get_sender_and_receiver_leaders(
        company_uuid=company.uuid,
        leaderboard_time_settings=company.leaderbord_time_settings,
        group_by_company_values=company.enable_company_values
    )

    app.client.views_publish(
        user_id=user_id,
        view=home_page_company_thank_yous_view(
            thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, last_n=20),
            current_user_slack_id=user_id,
            sender_leaders=senders_receivers_stats.sender_leaders,
            receiver_leaders=senders_receivers_stats.receiver_leaders,
            leaders_stats_from_date=senders_receivers_stats.leaders_stats_from_datetime.date(),
            leaders_stats_until_date=senders_receivers_stats.leaders_stats_until_datetime.date(),
            enable_leaderboard=company.enable_leaderboard,
        )
    )


def home_page_my_thank_you_button_clicked_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    app.client.views_publish(
        user_id=user_id,
        view=home_page_my_thank_yous_view(
            thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, author_slack_user_id=user_id,
                                                           last_n=20),
        )
    )


def home_page_say_thank_you_button_clicked_action_handler(body, logger):
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
        app.client.views_open(
            trigger_id=body["trigger_id"],
            view=thank_you_dialog_view(
                thank_you_types=dao.read_thank_you_types(company_uuid=company.uuid),
                enable_rich_text=company.enable_rich_text_in_thank_you_messages,
                enable_company_values=company.enable_company_values,
                max_receivers_num=company.receivers_number_limit,
                enable_attaching_files=company.enable_attaching_files,
                max_attached_files_num=company.max_attached_files_num,
                num_of_messages_a_user_can_send=num_of_messages_a_user_can_send,
            ),
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")
