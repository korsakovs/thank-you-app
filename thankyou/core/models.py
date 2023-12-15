import uuid

from dataclasses import dataclass, field
from datetime import datetime
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
class Company:
    name: str
    slack_team_id: Slack_Team_ID_Type
    uuid: UUID_Type = field(default_factory=lambda: str(uuid.uuid4()))
    deleted: bool = False


@dataclass
class ThankYouType:
    name: str
    company: Company
    uuid: UUID_Type = field(default_factory=lambda: str(uuid.uuid4()))
    deleted: bool = False


@dataclass
class ThankYouReceiver:
    slack_user_id: Slack_User_ID_Type


@dataclass
class ThankYouMessage:
    text: str
    company: Company

    type: Optional[ThankYouType] = None

    deleted: bool = False

    author_slack_user_id: Optional[Slack_User_ID_Type] = None
    author_slack_user_name: Optional[str] = None

    receivers: List[ThankYouReceiver] = field(default_factory=list)

    uuid: UUID_Type = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ThankYouStats:
    type: ThankYouType
    leader_slack_user_id: Slack_User_ID_Type
    leader_slack_messages_num: int
    total_messages_num: int
