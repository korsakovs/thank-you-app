import uuid

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List

UUID_Type = str
Slack_Team_ID_Type = str
Slack_User_ID_Type = str
Slack_Channel_ID_Type = str


@dataclass
class SlackUserInfo:
    name: str
    is_admin: bool
    is_owner: bool


@dataclass
class CompanyAdmin:
    company_uuid: str
    slack_user_id: Slack_User_ID_Type


class LeaderbordTimeSettings(Enum):
    LAST_30_DAYS = 1
    CURRENT_FULL_MONTH = 2
    LAST_FULL_MONTH = 3
    LAST_7_DAYS = 4
    LAST_FULL_WEEK = 5
    CURRENT_FULL_WEEK = 6


@dataclass
class Company:
    slack_team_id: Slack_Team_ID_Type

    # Config
    admins: List[CompanyAdmin]
    enable_sharing_in_a_slack_channel: bool
    share_messages_in_slack_channel: Optional[Slack_Channel_ID_Type]
    leaderbord_time_settings: LeaderbordTimeSettings
    enable_weekly_thank_you_limit: bool
    weekly_thank_you_limit: int
    receivers_number_limit: int
    enable_leaderboard: bool
    enable_private_message_counting_in_leaderboard: bool
    enable_company_values: bool
    enable_rich_text_in_thank_you_messages: bool
    enable_attaching_files: bool
    enable_private_messages: bool
    max_attached_files_num: int

    uuid: UUID_Type = field(default_factory=lambda: str(uuid.uuid4()))
    deleted: bool = False


@dataclass
class ThankYouType:
    name: str
    company_uuid: UUID_Type
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
    is_rich_text: bool
    is_private: bool

    type: Optional[ThankYouType] = None

    deleted: bool = False

    author_slack_user_id: Optional[Slack_User_ID_Type] = None

    slash_command_slack_channel_id: Optional[Slack_Channel_ID_Type] = None

    receivers: List[ThankYouReceiver] = field(default_factory=list)
    images: List[ThankYouMessageImage] = field(default_factory=list)

    uuid: UUID_Type = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def sorted_images(self) -> Optional[List[ThankYouMessageImage]]:
        if not self.images:
            return None
        return sorted(self.images, key=lambda i: i.ordering_key)


@dataclass
class ThankYouStats:
    type: ThankYouType
    leader_slack_user_id: Slack_User_ID_Type
    leader_slack_messages_num: int
    total_messages_num: int


@dataclass
class Employee:
    slack_user_id: Slack_User_ID_Type
    company_uuid: UUID_Type

    closed_welcome_message: bool = False

    uuid: UUID_Type = field(default_factory=lambda: str(uuid.uuid4()))
