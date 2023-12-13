import logging
from typing import Optional

from cachetools import TTLCache, cached
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

from thankyou.core.config import slack_app_token, slack_bot_token, get_env, Env
from thankyou.core.models import SlackUserInfo
from thankyou.dao import dao
from thankyou.slackbot.utils import get_or_create_company_by_event, get_or_create_company_by_slack_team_id
from thankyou.slackbot.views.homepage import home_page_my_updates_view

logging.basicConfig(level=logging.DEBUG if get_env() == Env.DEV else logging.INFO,
                    format="%(asctime)s %(levelname)s %(module)s - %(thread)d - %(message)s")
app = App(token=slack_bot_token())


@cached(cache=TTLCache(maxsize=1024 * 20, ttl=60 * 60))
def get_user_info(slack_user_id: str) -> Optional[SlackUserInfo]:
    user = app.client.users_info(user=slack_user_id)
    profile = user.data["user"]["profile"]

    name = None
    print("PROFILE:")
    print(profile)

    try:
        name = profile["display_name"]
    except (KeyError, TypeError):
        try:
            name = profile["real_name"]
        except (KeyError, TypeError):
            pass

    if name is None:
        return None

    return SlackUserInfo(
        name=name,
        is_admin=user.data["user"]["is_admin"],
        is_owner=user.data["user"]["is_owner"]
    )


@app.event("app_home_opened")
def home_page_open_handler(client: WebClient, event, logger):
    user_id = event["user"]
    user_info = get_user_info(user_id)
    is_admin = user_info and (user_info.is_admin or user_info.is_owner)
    try:
        company = get_or_create_company_by_event(event)
    except Exception:
        company = get_or_create_company_by_slack_team_id(client.default_params["team_id"])
    company_uuid = company.uuid

    view = home_page_my_updates_view(
        thank_you_messages=dao.read_thank_you_messages(company_uuid=company_uuid, author_slack_user_id=user_id,
                                                       last_n=20),
        is_admin=is_admin,
    )

    try:
        client.views_publish(
            user_id=user_id,
            view=view
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    handler = SocketModeHandler(app, slack_app_token())
    handler.start()

