from threading import Lock
from typing import Optional

from thankyou.core.models import Company, LeaderbordTimeSettings
from thankyou.dao import dao, create_initial_data

CREATE_COMPANY_LOCK = Lock()


def get_or_create_company_by_slack_team_id(slack_team_id: str, new_name: str = None) -> Company:
    companies = dao.read_companies(slack_team_id=slack_team_id)
    try:
        return companies[0]
    except IndexError:
        with CREATE_COMPANY_LOCK:
            try:
                return dao.read_companies(slack_team_id=slack_team_id)[0]
            except IndexError:
                company = Company(
                    slack_team_id=slack_team_id,
                    name=new_name or "",
                    admins=[],
                    enable_sharing_in_a_slack_channel=False,
                    share_messages_in_slack_channel=None,
                    leaderbord_time_settings=LeaderbordTimeSettings.LAST_30_DAYS,
                    enable_weekly_thank_you_limit=True,
                    weekly_thank_you_limit=5,
                    receivers_number_limit=10,
                    enable_leaderboard=True,
                    enable_company_values=True,
                    enable_rich_text_in_thank_you_messages=False,
                    enable_attaching_files=True,
                    enable_private_messages=False,
                    max_attached_files_num=5,
                )
                dao.create_company(company)
                create_initial_data(company)
                return company


def get_or_create_company_by_body(body) -> Company:
    try:
        slack_team_id = body["team"]["id"]
    except KeyError:
        slack_team_id = body["team_id"]
    if not slack_team_id:
        raise Exception(f"Can not find slack_team_id in a body: {body}")

    return get_or_create_company_by_slack_team_id(slack_team_id, slack_team_id)


def get_or_create_company_by_event(event) -> Optional[Company]:
    slack_team_id = event["view"]["team_id"]
    if not slack_team_id:
        raise Exception(f"Can not find slack_team_id in event: {event}")
    return get_or_create_company_by_slack_team_id(slack_team_id)
