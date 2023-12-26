from abc import ABC, abstractmethod
from datetime import datetime

from typing import List, Optional, Tuple

from thankyou.core.models import Company, ThankYouMessage, ThankYouType, Slack_User_ID_Type, CompanyAdmin


class Dao(ABC):
    @abstractmethod
    def create_thank_you_message(self, thank_you_message: ThankYouMessage): ...

    @abstractmethod
    def read_thank_you_message(self, company_uuid: str, thank_you_message_uuid: str) -> Optional[ThankYouMessage]: ...

    @abstractmethod
    def read_thank_you_messages(self, company_uuid: str, created_after: datetime = None,
                                created_before: datetime = None, with_types: List[str] = None,
                                deleted: Optional[bool] = False, author_slack_user_id: str = None,
                                receiver_slack_user_id: str = None, last_n: int = None
                                ) -> List[ThankYouMessage]: ...

    @abstractmethod
    def delete_thank_you_message(self, company_uuid: str, thank_you_message_uuid: str): ...

    @abstractmethod
    def create_company(self, company: Company): ...

    @abstractmethod
    def read_company(self, company_uuid: str) -> Optional[Company]: ...

    @abstractmethod
    def read_companies(self, company_name: str = None, slack_team_id: str = None, deleted: Optional[bool] = False) \
        -> List[Company]: ...

    @abstractmethod
    def create_company_admin(self, company_admin: CompanyAdmin): ...

    @abstractmethod
    def delete_company_admin(self, company_uuid: str, slack_user_id: str): ...

    @abstractmethod
    def create_thank_you_type(self, thank_you_type: ThankYouType): ...

    @abstractmethod
    def read_thank_you_type(self, company_uuid: str, thank_you_type_uuid: str) -> Optional[ThankYouType]: ...

    @abstractmethod
    def read_thank_you_types(self, company_uuid: str, name: str = None, deleted: Optional[bool] = False) \
        -> List[ThankYouType]: ...

    @abstractmethod
    def delete_thank_you_type(self, company_uuid: str, thank_you_type_uuid: str): ...

    @abstractmethod
    def get_thank_you_sender_leaders(self, company_uuid: str, created_after: datetime = None,
                                     created_before: datetime = None, thank_you_type: ThankYouType = None,
                                     leaders_num: int = 3) -> List[Tuple[Slack_User_ID_Type, int]]: ...

    @abstractmethod
    def get_thank_you_receiver_leaders(self, company_uuid: str, created_after: datetime = None,
                                       created_before: datetime = None, thank_you_type: ThankYouType = None,
                                       leaders_num: int = 3) -> List[Tuple[Slack_User_ID_Type, int]]: ...
