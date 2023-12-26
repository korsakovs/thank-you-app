from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Tuple, List

from cachetools import TTLCache, cached

from thankyou.core.models import SlackUserInfo, LeaderbordTimeSettings, ThankYouType, CompanyAdmin, Company
from thankyou.dao import dao
from thankyou.slackbot.app import app
from thankyou.slackbot.views.configuration import configuration_no_access_view, configuration_view


_already_invited_to_a_channel = TTLCache(maxsize=1024 * 20, ttl=10 * 60)


def already_invited_to_a_channel(company_id: str, channel: str, user_id: str):
    key = "++".join((company_id, channel, user_id))

    global _already_invited_to_a_channel

    if key in _already_invited_to_a_channel:
        return True

    _already_invited_to_a_channel[key] = True
    return False


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


def is_user_an_admin(company_admins: List[CompanyAdmin], slack_user_id: str):
    result = slack_user_id in [admin.slack_user_id for admin in company_admins]
    if not result:
        user_info = get_user_info(slack_user_id)
        result = user_info and (user_info.is_admin or user_info.is_owner)
    return result


@dataclass
class SendersReceiversStats:
    leaders_stats_from_datetime: datetime
    leaders_stats_until_datetime: datetime
    sender_leaders: List[Tuple[Optional[ThankYouType], List[Tuple[str, int]]]]
    receiver_leaders: List[Tuple[Optional[ThankYouType], List[Tuple[str, int]]]]


@cached(cache=TTLCache(maxsize=1024, ttl=60))
def get_sender_and_receiver_leaders(company_uuid: str, leaderboard_time_settings: LeaderbordTimeSettings,
                                    group_by_company_values: bool) -> SendersReceiversStats:
    if leaderboard_time_settings == LeaderbordTimeSettings.LAST_30_DAYS:
        leaders_stats_from_datetime = datetime.utcnow() - timedelta(days=30)
        leaders_stats_until_datetime = datetime.utcnow()
    elif leaderboard_time_settings == LeaderbordTimeSettings.LAST_7_DAYS:
        leaders_stats_from_datetime = datetime.utcnow() - timedelta(days=7)
        leaders_stats_until_datetime = datetime.utcnow()
    elif leaderboard_time_settings == LeaderbordTimeSettings.CURRENT_FULL_MONTH:
        leaders_stats_from_datetime = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        leaders_stats_until_datetime = ((leaders_stats_from_datetime + timedelta(days=45))
                                        .replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                                        - timedelta(microseconds=1))
    elif leaderboard_time_settings == LeaderbordTimeSettings.LAST_FULL_MONTH:
        leaders_stats_from_datetime = (datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                                       - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        leaders_stats_until_datetime = (datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                                        - timedelta(microseconds=1))
    elif leaderboard_time_settings == LeaderbordTimeSettings.LAST_FULL_WEEK:
        leaders_stats_until_datetime = (datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                                        - timedelta(days=datetime.utcnow().weekday()))
        leaders_stats_from_datetime = leaders_stats_until_datetime - timedelta(weeks=1)
        leaders_stats_until_datetime = leaders_stats_until_datetime - timedelta(microseconds=1)
    else:
        raise ValueError(f"Unknown leaderboard time settings: {leaderboard_time_settings}")
    sender_leaders = []
    receiver_leaders = []
    if not group_by_company_values:
        sender_leaders.append((None, dao.get_thank_you_sender_leaders(
            company_uuid=company_uuid,
            created_after=leaders_stats_from_datetime,
            created_before=leaders_stats_until_datetime
        )))
        receiver_leaders.append((None, dao.get_thank_you_receiver_leaders(
            company_uuid=company_uuid,
            created_after=leaders_stats_from_datetime,
            created_before=leaders_stats_until_datetime
        )))
    else:
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
    return SendersReceiversStats(
        leaders_stats_from_datetime=leaders_stats_from_datetime,
        leaders_stats_until_datetime=leaders_stats_until_datetime,
        sender_leaders=sender_leaders,
        receiver_leaders=receiver_leaders
    )


def publish_configuration_view(company: Company, user_id: str):
    is_admin = is_user_an_admin(company_admins=company.admins, slack_user_id=user_id)

    if not is_admin:
        view = configuration_no_access_view(admin_slack_ids=[admin.slack_user_id for admin in company.admins])
    else:
        view = configuration_view(
            thank_you_types=dao.read_thank_you_types(company_uuid=company.uuid),
            admin_slack_user_ids=[admin.slack_user_id for admin in company.admins],
            leaderbord_time_settings=company.leaderbord_time_settings,
            enable_sharing_in_a_slack_channel=company.enable_sharing_in_a_slack_channel,
            share_messages_in_slack_channel=company.share_messages_in_slack_channel,
            enable_weekly_thank_you_limit=company.enable_weekly_thank_you_limit,
            weekly_thank_you_limit=company.weekly_thank_you_limit,
            enable_rich_text_in_thank_you_messages=company.enable_rich_text_in_thank_you_messages,
            enable_company_values=company.enable_company_values,
            enable_leaderboard=company.enable_leaderboard,
            max_thank_you_receivers_num=company.receivers_number_limit,
            enable_attaching_files=company.enable_attaching_files,
            max_attached_files_num=company.max_attached_files_num,
        )

    app.client.views_publish(
        user_id=user_id,
        view=view
    )
