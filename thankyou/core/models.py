import uuid

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List

UUID_Type = str
Slack_Team_ID_Type = str
Slack_User_ID_Type = str


@dataclass
class SlackUserInfo:
    name: str
    is_admin: bool
    is_owner: bool


@dataclass
class CompanyAdmin:
    slack_user_id: Slack_User_ID_Type


class LeaderbordTimeSettings(Enum):
    LAST_30_DAYS = 1
    LAST_FULL_MONTH = 2
    LAST_7_DAYS = 3
    LAST_FULL_WEEK = 4


@dataclass
class Company:
    name: str
    slack_team_id: Slack_Team_ID_Type
    uuid: UUID_Type = field(default_factory=lambda: str(uuid.uuid4()))
    deleted: bool = False

    # Config
    admins: List[CompanyAdmin] = field(default_factory=lambda: list())
    share_messages_in_slack_channel = None
    leaderbord_time_settings: LeaderbordTimeSettings = LeaderbordTimeSettings.LAST_30_DAYS
    weekly_thank_you_limit: int = 5


@dataclass
class ThankYouType:
    name: str
    company_uuid: UUID_Type
    company: Company
    uuid: UUID_Type = field(default_factory=lambda: str(uuid.uuid4()))
    deleted: bool = False


@dataclass
class ThankYouReceiver:
    slack_user_id: Slack_User_ID_Type


@dataclass
class ThankYouMessageImage:
    url: str
    filename: str
    ordering_key: int
    uuid: UUID_Type = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ThankYouMessage:
    text: str
    company: Company

    type: Optional[ThankYouType] = None

    deleted: bool = False

    author_slack_user_id: Optional[Slack_User_ID_Type] = None
    author_slack_user_name: Optional[str] = None

    receivers: List[ThankYouReceiver] = field(default_factory=list)
    images: List[ThankYouMessageImage] = field(default_factory=list)

    uuid: UUID_Type = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ThankYouStats:
    type: ThankYouType
    leader_slack_user_id: Slack_User_ID_Type
    leader_slack_messages_num: int
    total_messages_num: int
