import datetime
import logging
from typing import Optional

from cachetools import TTLCache, cached
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

from thankyou.core.config import slack_app_token, slack_bot_token, get_env, Env
from thankyou.core.models import SlackUserInfo
from thankyou.dao import dao
from thankyou.slackbot.utils.company import get_or_create_company_by_event, get_or_create_company_by_slack_team_id, \
    get_or_create_company_by_body
from thankyou.slackbot.utils.privatemetadata import retrieve_thank_you_message_from_body
from thankyou.slackbot.views.homepage import home_page_company_thank_yous_view, home_page_my_thank_yous_view
from thankyou.slackbot.views.thankyoudialog import thank_you_dialog_view

logging.basicConfig(level=logging.DEBUG if get_env() == Env.DEV else logging.INFO,
                    format="%(asctime)s %(levelname)s %(module)s - %(thread)d - %(message)s")
app = App(token=slack_bot_token())


@cached(cache=TTLCache(maxsize=1024 * 20, ttl=60 * 60))
def get_user_info(slack_user_id: str) -> Optional[SlackUserInfo]:
    user = app.client.users_info(user=slack_user_id)
    try:
        user_data = user.data["user"]
        profile = user_data["profile"]
    except (KeyError, TypeError):
        return None

    name = None

    for prefix in (
        "display_name",
        "real_name",
    ):
        try:
            name = profile[prefix]
        except (KeyError, TypeError):
            pass

        if name:
            break
        else:
            name = None

    if name:
        return SlackUserInfo(
            name=str(name),
            is_admin=bool(user_data["is_admin"]),
            is_owner=bool(user_data["is_owner"])
        )


@app.event("app_home_opened")
def app_home_opened_action_handler(client: WebClient, event, logger):
    user_id = event["user"]
    user_info = get_user_info(user_id)
    is_admin = user_info and (user_info.is_admin or user_info.is_owner)
    try:
        company = get_or_create_company_by_event(event)
    except Exception:
        company = get_or_create_company_by_slack_team_id(client.default_params["team_id"])

    sender_leaders = []
    receiver_leaders = []
    leaders_stats_from_datetime = datetime.datetime.utcnow() - datetime.timedelta(days=30)
    for thank_you_type in dao.read_thank_you_types(company_uuid=company.uuid):
        type_leaders = dao.get_thank_you_sender_leaders(
            company_uuid=company.uuid,
            thank_you_type=thank_you_type,
            created_after=datetime.datetime.utcnow() - datetime.timedelta(days=30)
        )
        sender_leaders.append((thank_you_type, type_leaders))
        type_leaders = dao.get_thank_you_receiver_leaders(
            company_uuid=company.uuid,
            thank_you_type=thank_you_type,
            created_after=datetime.datetime.utcnow() - datetime.timedelta(days=30)
        )
        receiver_leaders.append((thank_you_type, type_leaders))

    view = home_page_company_thank_yous_view(
        thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, author_slack_user_id=user_id,
                                                       last_n=20),
        sender_leaders=sender_leaders,
        receiver_leaders=receiver_leaders,
        leaders_stats_from_date=leaders_stats_from_datetime.date(),
        leaders_stats_until_date=datetime.datetime.utcnow().date(),
        is_admin=is_admin,
        current_user_slack_id=user_id
    )

    client.views_publish(
        user_id=user_id,
        view=view
    )


@app.action("home_page_company_thank_you_button_clicked")
def home_page_company_thank_you_button_clicked_action_handler(ack, body, logger):
    ack()
    logger.info(body)
    user_id = body["user"]["id"]
    user_info = get_user_info(user_id)
    company = get_or_create_company_by_body(body)

    app.client.views_publish(
        user_id=user_id,
        view=home_page_company_thank_yous_view(
            thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, last_n=20),
            is_admin=user_info.is_admin,
            current_user_slack_id=user_id
        )
    )


@app.action("home_page_my_thank_you_button_clicked")
def home_page_my_thank_you_button_clicked_action_handler(ack, body, logger):
    ack()
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


@app.action("home_page_say_thank_you_button_clicked")
def home_page_say_thank_you_button_clicked_action_handler(ack, body, logger):
    ack()
    company_uuid = get_or_create_company_by_body(body).uuid

    try:
        app.client.views_open(
            trigger_id=body["trigger_id"],
            view=thank_you_dialog_view(thank_you_types=dao.read_thank_you_types(company_uuid=company_uuid)),
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


@app.view("thank_you_dialog_save_button_clicked")
def thank_you_dialog_save_button_clicked_action_handler(ack, body, logger):
    ack()
    logger.info(body)
    thank_you_message = retrieve_thank_you_message_from_body(body)
    dao.create_thank_you_message(thank_you_message)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    handler = SocketModeHandler(app, slack_app_token())
    handler.start()

