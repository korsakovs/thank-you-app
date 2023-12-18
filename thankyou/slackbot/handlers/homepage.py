from datetime import datetime, timedelta

from slack_sdk import WebClient

from thankyou.dao import dao
from thankyou.slackbot.app import app
from thankyou.slackbot.handlers.common import get_user_info, get_sender_and_receiver_leaders
from thankyou.slackbot.utils.company import get_or_create_company_by_event, get_or_create_company_by_slack_team_id, \
    get_or_create_company_by_body
from thankyou.slackbot.views.homepage import home_page_company_thank_yous_view, home_page_my_thank_yous_view
from thankyou.slackbot.views.thankyoudialog import thank_you_dialog_view


def app_home_opened_action_handler(client: WebClient, event, logger):
    user_id = event["user"]
    user_info = get_user_info(user_id)
    is_admin = user_info and (user_info.is_admin or user_info.is_owner)
    try:
        company = get_or_create_company_by_event(event)
    except Exception:
        company = get_or_create_company_by_slack_team_id(client.default_params["team_id"])

    view = home_page_company_thank_yous_view(
        thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, author_slack_user_id=user_id,
                                                       last_n=20),
        is_admin=is_admin,
        current_user_slack_id=user_id
    )

    client.views_publish(
        user_id=user_id,
        view=view
    )


def home_page_company_thank_you_button_clicked_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    user_info = get_user_info(user_id)
    company = get_or_create_company_by_body(body)

    app.client.views_publish(
        user_id=user_id,
        view=home_page_company_thank_yous_view(
            thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, last_n=20),
            is_admin=user_info.is_admin,
            current_user_slack_id=user_id,
        )
    )


def home_page_show_leaders_button_clicked_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    user_info = get_user_info(user_id)
    company = get_or_create_company_by_body(body)

    sender_leaders, receiver_leaders = get_sender_and_receiver_leaders(company_uuid=company.uuid)

    app.client.views_publish(
        user_id=user_id,
        view=home_page_company_thank_yous_view(
            thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, last_n=20),
            is_admin=user_info.is_admin,
            current_user_slack_id=user_id,
            sender_leaders=sender_leaders,
            receiver_leaders=receiver_leaders,
            leaders_stats_from_date=(datetime.utcnow() - timedelta(days=30)).date(),
            leaders_stats_until_date=datetime.utcnow().date(),
        )
    )


def home_page_my_thank_you_button_clicked_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    user_info = get_user_info(user_id)
    company = get_or_create_company_by_body(body)

    app.client.views_publish(
        user_id=user_id,
        view=home_page_my_thank_yous_view(
            thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, author_slack_user_id=user_id,
                                                           last_n=20),
            is_admin=user_info.is_admin
        )
    )


def home_page_say_thank_you_button_clicked_action_handler(body, logger):
    company_uuid = get_or_create_company_by_body(body).uuid

    try:
        app.client.views_open(
            trigger_id=body["trigger_id"],
            view=thank_you_dialog_view(thank_you_types=dao.read_thank_you_types(company_uuid=company_uuid)),
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")
