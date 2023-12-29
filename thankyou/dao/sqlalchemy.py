from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional, Generator, Tuple

from sqlalchemy import Engine, MetaData, Column, Table, String, ForeignKey, Boolean, Text, DateTime, or_, desc, \
    and_, func, Integer, Enum
from sqlalchemy.orm import registry, relationship, sessionmaker, Session

from thankyou.core.models import ThankYouType, Company, ThankYouMessage, ThankYouReceiver, \
    ThankYouMessageImage, Slack_User_ID_Type, CompanyAdmin, LeaderbordTimeSettings
from thankyou.dao.interface import Dao


class SQLAlchemyDao(Dao, ABC):
    _COMPANY_ADMINS_TABLE = "company_admins"
    _COMPANIES_TABLE = "companies"
    _THANK_YOU_MESSAGES_TABLE = "thank_you_messages"
    _THANK_YOU_TYPES_TABLE = "thank_you_types"
    _THANK_YOU_RECEIVERS_TABLE = "thank_you_receivers"
    _THANK_YOU_MESSAGE_IMAGES = "thank_you_message_images"

    @abstractmethod
    def _create_engine(self) -> Engine:
        ...

    def __init__(self):
        self._mapper_registry = registry()
        self._metadata_obj = MetaData()

        self._company_admins_table = Table(
            self._COMPANY_ADMINS_TABLE,
            self._metadata_obj,
            Column("company_uuid", String(256), ForeignKey(f"{self._COMPANIES_TABLE}.uuid"),
                   primary_key=True, nullable=False),
            Column("slack_user_id", String(256), primary_key=True, nullable=False)
        )

        self._companies_table = Table(
            self._COMPANIES_TABLE,
            self._metadata_obj,
            Column("uuid", String(256), primary_key=True, nullable=False),
            Column("slack_team_id", String(256), nullable=False, unique=True, index=True),
            Column("name", String(256), nullable=False),
            Column("deleted", Boolean, nullable=False),
            Column("enable_sharing_in_a_slack_channel", Boolean, nullable=False),
            Column("share_messages_in_slack_channel", String(256), nullable=True),
            Column("leaderbord_time_settings", Enum(LeaderbordTimeSettings), nullable=False),
            Column("enable_weekly_thank_you_limit", Boolean, nullable=False),
            Column("weekly_thank_you_limit", Integer, nullable=False),
            Column("receivers_number_limit", Integer, nullable=False),
            Column("enable_leaderboard", Boolean, nullable=False),
            Column("enable_company_values", Boolean, nullable=False),
            Column("enable_rich_text_in_thank_you_messages", Boolean, nullable=False),
            Column("enable_attaching_files", Boolean, nullable=False),
            Column("max_attached_files_num", Integer, nullable=False),
        )

        self._thank_you_types_table = Table(
            self._THANK_YOU_TYPES_TABLE,
            self._metadata_obj,
            Column("uuid", String(256), primary_key=True, nullable=False),
            Column("name", String(256), nullable=False),
            Column("company_uuid", String(256), ForeignKey(f"{self._COMPANIES_TABLE}.uuid"), nullable=False),
            Column("deleted", Boolean, nullable=False),
        )

        self._thank_you_messages_table = Table(
            self._THANK_YOU_MESSAGES_TABLE,
            self._metadata_obj,
            Column("uuid", String(256), primary_key=True, nullable=False),
            Column("company_uuid", String(256), ForeignKey(f"{self._COMPANIES_TABLE}.uuid"),
                   nullable=False, index=True),
            Column("deleted", Boolean, nullable=False),
            Column("text", Text, nullable=False),
            Column("is_rich_text", Boolean, nullable=False),
            Column("author_slack_user_id", String(256), nullable=False, index=True),
            Column("author_slack_user_name", String(256), nullable=True),
            Column("created_at", DateTime, nullable=False, index=True),
            Column("thank_you_type_uuid", String(256), ForeignKey(f"{self._THANK_YOU_TYPES_TABLE}.uuid"),
                   nullable=True, index=True),
        )

        self._thank_you_receivers_table = Table(
            self._THANK_YOU_RECEIVERS_TABLE,
            self._metadata_obj,
            Column("thank_you_message_uuid", String(256), ForeignKey(f"{self._THANK_YOU_MESSAGES_TABLE}.uuid"),
                   primary_key=True, nullable=False),
            Column("slack_user_id", String(256), primary_key=True, nullable=False, index=True),
        )

        self._thank_you_message_images_table = Table(
            self._THANK_YOU_MESSAGE_IMAGES,
            self._metadata_obj,
            Column("uuid", String(256), primary_key=True, nullable=False),
            Column("thank_you_message_uuid", String(256), ForeignKey(f"{self._THANK_YOU_MESSAGES_TABLE}.uuid"),
                   nullable=False, index=True),
            Column("url", String(1024), nullable=False),
            Column("filename", String(1024), nullable=False),
            Column("ordering_key", Integer, nullable=False),
        )

        self._mapper_registry.map_imperatively(CompanyAdmin, self._company_admins_table)

        self._mapper_registry.map_imperatively(Company, self._companies_table, properties={
            "admins": relationship(CompanyAdmin)
        })

        self._mapper_registry.map_imperatively(ThankYouType, self._thank_you_types_table, properties={
            "company": relationship(Company)
        })

        self._mapper_registry.map_imperatively(
            ThankYouMessage,
            self._thank_you_messages_table,
            properties={
                "company": relationship(Company),
                "type": relationship(ThankYouType),
                "receivers": relationship(ThankYouReceiver),
                "images": relationship(ThankYouMessageImage),
            }
        )

        self._mapper_registry.map_imperatively(ThankYouReceiver, self._thank_you_receivers_table)
        self._mapper_registry.map_imperatively(ThankYouMessageImage, self._thank_you_message_images_table)

        self._engine = self._create_engine()
        self._metadata_obj.create_all(bind=self._engine, checkfirst=True)
        self._session_maker = sessionmaker(bind=self._engine)
        self._session = self._session_maker()

    @contextmanager
    def _get_session(self) -> Generator[Session, None, None]:
        """
        with self._session_maker() as session:
            yield session
            session.commit()
        """
        yield self._session
        self._session.commit()

    @property
    def engine(self) -> Engine:
        return self._engine

    def _get_obj(self, cls, uuid):
        with self._get_session() as session:
            return session.get(cls, uuid)

    def _set_obj(self, obj):
        with self._get_session() as session:
            session.merge(obj, load=True)

    def create_thank_you_message(self, thank_you_message: ThankYouMessage):
        self._set_obj(thank_you_message)

    def read_thank_you_message(self, company_uuid: str, thank_you_message_uuid: str) -> Optional[ThankYouMessage]:
        thank_you_message: ThankYouMessage = self._get_obj(ThankYouMessage, thank_you_message_uuid)
        if thank_you_message and thank_you_message.company.uuid == company_uuid:
            return thank_you_message

    def read_thank_you_messages(self, company_uuid: str, created_after: datetime = None,
                                created_before: datetime = None, with_types: List[str] = None,
                                deleted: Optional[bool] = False, author_slack_user_id: str = None,
                                receiver_slack_user_id: str = None, last_n: int = None
                                ) -> List[ThankYouMessage]:
        with self._get_session() as session:
            result = session.query(ThankYouMessage).join(Company)
            if receiver_slack_user_id:
                result = result.join(ThankYouReceiver)
                result = result.filter(ThankYouReceiver.slack_user_id == receiver_slack_user_id)

            result = result.filter(Company.uuid == company_uuid)

            if created_after:
                result = result.filter(ThankYouMessage.created_at >= created_after)

            if created_before:
                result = result.filter(ThankYouMessage.created_at <= created_before)

            if with_types:
                result = result.filter(or_(ThankYouMessage.type == type_ for type_ in with_types))

            if deleted is not None:
                result = result.filter(ThankYouMessage.deleted == deleted)

            if author_slack_user_id is not None:
                result = result.filter(ThankYouMessage.author_slack_user_id == author_slack_user_id)

            # noinspection PyTypeChecker
            result = result.order_by(desc(ThankYouMessage.created_at))

            if last_n is not None:
                result = result.limit(last_n)

            return result.distinct().all()

    def delete_thank_you_message(self, company_uuid: str, thank_you_message_uuid: str):
        with self._get_session() as session:
            session.quert(ThankYouMessage).join(Company).filter(
                and_(ThankYouMessage.uuid == thank_you_message_uuid, Company.uuid == company_uuid)).update(
                {
                    ThankYouMessage.deleted: True
                },
                synchronize_session=False)

    def create_company(self, company: Company):
        self._set_obj(company)

    def read_company(self, company_uuid: str) -> Optional[Company]:
        return self._get_obj(Company, company_uuid)

    def read_companies(self, company_name: str = None, slack_team_id: str = None, deleted: Optional[bool] = False) \
            -> List[Company]:
        with self._get_session() as session:
            result = session.query(Company)
            if company_name is not None:
                result = result.filter(Company.name == company_name)
            if slack_team_id is not None:
                result = result.filter(Company.slack_team_id == slack_team_id)
            if deleted is not None:
                result = result.filter(Company.deleted == deleted)
            return result.all()

    def create_company_admin(self, company_admin: CompanyAdmin):
        self._set_obj(company_admin)

    def delete_company_admin(self, company_uuid: str, slack_user_id: str):
        with self._get_session() as session:
            session.query(CompanyAdmin).where(and_(
                CompanyAdmin.company_uuid == company_uuid,
                CompanyAdmin.slack_user_id == slack_user_id
            )).delete()

    def create_thank_you_type(self, thank_you_type: ThankYouType):
        self._set_obj(thank_you_type)

    def read_thank_you_type(self, company_uuid: str, thank_you_type_uuid: str) -> Optional[ThankYouType]:
        thank_you_type: ThankYouType = self._get_obj(ThankYouType, thank_you_type_uuid)
        if thank_you_type and thank_you_type.company_uuid == company_uuid:
            return thank_you_type

    def read_thank_you_types(self, company_uuid: str, name: str = None, deleted: Optional[bool] = False) \
            -> List[ThankYouType]:
        with self._get_session() as session:
            result = session.query(ThankYouType)
            result = result.join(Company).filter(Company.uuid == company_uuid)
            if deleted is not None:
                result = result.filter(ThankYouType.deleted == deleted)
            if name:
                result = result.filter(ThankYouType.name == name)
            return result.all()

    def delete_thank_you_type(self, company_uuid: str, thank_you_type_uuid: str):
        with self._get_session() as session:
            session.query(ThankYouType).filter(and_(ThankYouType.uuid == thank_you_type_uuid, ThankYouType.uuid.in_(
                session.query(ThankYouType.uuid).join(Company).filter(Company.uuid == company_uuid)
            ))).update({
                ThankYouType.deleted: True
            }, synchronize_session=False)

    def get_thank_you_sender_leaders(self, company_uuid: str, created_after: datetime = None,
                                     created_before: datetime = None, thank_you_type: ThankYouType = None,
                                     leaders_num: int = 3) -> List[Tuple[Slack_User_ID_Type, int]]:
        with self._get_session() as session:
            result = session.query(ThankYouMessage.author_slack_user_id, func.count())
            result = result.filter(ThankYouMessage.deleted == False)
            result = result.join(Company).filter(Company.uuid == company_uuid)

            if created_after:
                result = result.filter(ThankYouMessage.created_at > created_after)

            if created_before:
                result = result.filter(ThankYouMessage.created_at <= created_before)

            if thank_you_type:
                result = result.filter(ThankYouMessage.type == thank_you_type)

            result = result.group_by(ThankYouMessage.author_slack_user_id)
            result = result.order_by(func.count().desc())
            result = result.limit(leaders_num)

            return result.all()

    def get_thank_you_receiver_leaders(self, company_uuid: str, created_after: datetime = None,
                                       created_before: datetime = None, thank_you_type: ThankYouType = None,
                                       leaders_num: int = 3) -> List[Tuple[Slack_User_ID_Type, int]]:
        with self._get_session() as session:
            result = session.query(ThankYouReceiver.slack_user_id, func.count()).join(ThankYouMessage)
            result = result.filter(ThankYouMessage.deleted == False)
            result = result.join(Company).filter(Company.uuid == company_uuid)

            if created_after:
                result = result.filter(ThankYouMessage.created_at >= created_after)

            if created_before:
                result = result.filter(ThankYouMessage.created_at <= created_before)

            if thank_you_type:
                result = result.filter(ThankYouMessage.type == thank_you_type)

            result = result.group_by(ThankYouReceiver.slack_user_id)
            result = result.order_by(func.count().desc())
            result = result.limit(leaders_num)

            return result.all()
