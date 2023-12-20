from datetime import datetime, timedelta
from typing import Optional

from cachetools import TTLCache, cached

from thankyou.core.models import SlackUserInfo
from thankyou.dao import dao
from thankyou.slackbot.app import app


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


@cached(cache=TTLCache(maxsize=1024, ttl=60))
def get_sender_and_receiver_leaders(company_uuid: str):
    leaders_stats_from_datetime = datetime.utcnow() - timedelta(days=30)
    leaders_stats_until_datetime = datetime.utcnow()
    sender_leaders = []
    receiver_leaders = []
    for thank_you_type in dao.read_thank_you_types(company_uuid=company_uuid):
        type_leaders = dao.get_thank_you_sender_leaders(
            company_uuid=company_uuid,
            thank_you_type=thank_you_type,
            created_after=leaders_stats_from_datetime,
            created_before=leaders_stats_until_datetime
        )
        sender_leaders.append((thank_you_type, type_leaders))
        type_leaders = dao.get_thank_you_receiver_leaders(
            company_uuid=company_uuid,
            thank_you_type=thank_you_type,
            created_after=leaders_stats_from_datetime,
            created_before=leaders_stats_until_datetime
        )
        receiver_leaders.append((thank_you_type, type_leaders))
    return sender_leaders, receiver_leaders
