from threading import Lock
from typing import Optional

from thankyou.core.models import Company
from thankyou.dao import dao, create_initial_data

CREATE_COMPANY_LOCK = Lock()


def escape_string(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


es = escape_string


def get_or_create_company_by_slack_team_id(slack_team_id: str, new_name: str = None) -> Company:
    companies = dao.read_companies(slack_team_id=slack_team_id)
    try:
        return companies[0]
    except IndexError:
        with CREATE_COMPANY_LOCK:
            try:
                return dao.read_companies(slack_team_id=slack_team_id)[0]
            except IndexError:
                company = Company(slack_team_id=slack_team_id, name=new_name or "")
                dao.create_company(company)
                create_initial_data(company)
                return company


def get_or_create_company_by_event(event) -> Optional[Company]:
    slack_team_id = event["view"]["team_id"]
    if not slack_team_id:
        raise Exception(f"Can not find slack_team_id in event: {event}")
    return get_or_create_company_by_slack_team_id(slack_team_id)
