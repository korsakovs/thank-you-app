from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from typing import List, Optional

from thankyou.core.models import Company, ThankYouMessage, ThankYouType


class Dao(ABC):
    @abstractmethod
    def create_thank_you_message(self, thank_you_message: ThankYouMessage): ...

    @abstractmethod
    def publish_thank_you_message(self, company_uuid: str, thank_you_message_uuid: str) -> bool: ...

    def read_last_unpublished_thank_you_message(self, company_uuid: str, author_slack_user_uuid: str,
                                                no_older_than: timedelta = timedelta(days=30)) \
            -> Optional[ThankYouMessage]:
        updates = self.read_thank_you_messages(
            company_uuid=company_uuid,
            created_after=datetime.utcnow() - no_older_than,
            author_slack_user_uuid=author_slack_user_uuid,
            published=False
        )
        if updates:
            return max(updates, key=lambda message: message.created_at)

    @abstractmethod
    def read_thank_you_message(self, company_uuid: str, thank_you_message_uuid: str) -> Optional[ThankYouMessage]: ...

    @abstractmethod
    def read_thank_you_messages(self, company_uuid: str, created_after: datetime = None,
                                created_before: datetime = None, with_types: List[str] = None,
                                published: Optional[bool] = True, deleted: Optional[bool] = False,
                                author_slack_user_uuid: str = None, last_n: int = None) -> List[ThankYouMessage]: ...

    @abstractmethod
    def delete_thank_you_message(self, company_uuid: str, thank_you_message_uuid: str): ...

    @abstractmethod
    def create_company(self, company: Company): ...

    @abstractmethod
    def read_company(self, company_uuid: str) -> Optional[Company]: ...

    @abstractmethod
    def read_companies(self, company_name: str = None, slack_team_id: str = None) -> List[Company]: ...

    @abstractmethod
    def create_thank_you_type(self, thank_you_type: ThankYouType): ...

    @abstractmethod
    def read_thank_you_type(self, company_uuid: str, thank_you_type_uuid: str) -> Optional[ThankYouType]: ...

    @abstractmethod
    def read_thank_you_types(self, company_uuid: str, name: str = None) -> List[ThankYouType]: ...

    @abstractmethod
    def delete_thank_you_type(self, company_uuid: str, thank_you_type_uuid: str): ...
