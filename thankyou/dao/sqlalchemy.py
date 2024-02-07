import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional, Generator, Tuple

from sqlalchemy import Engine, MetaData, Column, Table, String, ForeignKey, Boolean, Text, DateTime, or_, desc, \
    and_, func, Integer, Enum, false, UniqueConstraint
from sqlalchemy.orm import registry, relationship, sessionmaker, Session, scoped_session
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from thankyou.core.models import ThankYouType, Company, ThankYouMessage, ThankYouReceiver, \
    ThankYouMessageImage, Slack_User_ID_Type, CompanyAdmin, LeaderbordTimeSettings, UUID_Type, Employee
from thankyou.dao.interface import Dao


logging.basicConfig(level=logging.DEBUG)


class SQLAlchemyDao(Dao, ABC):
    _COMPANY_ADMINS_TABLE = "company_admins"
    _COMPANIES_TABLE = "companies"
    _THANK_YOU_MESSAGES_TABLE = "thank_you_messages"
    _THANK_YOU_TYPES_TABLE = "thank_you_types"
    _THANK_YOU_RECEIVERS_TABLE = "thank_you_receivers"
    _THANK_YOU_MESSAGE_IMAGES = "thank_you_message_images"
    _EMPLOYEES_TABLE = "employees"

    @abstractmethod
    def _create_engine(self) -> Engine:
        ...

    def encrypted_text_column(self):
        if not self.secret_key:
            return Text
        return StringEncryptedType(Text, key=self.secret_key, engine=AesEngine)

    def encrypted_string_column(self, length: int):
        if not self.secret_key:
            return String(length)
        return StringEncryptedType(String(length), key=self.secret_key, engine=AesEngine)

    def __init__(self, encryption_secret_key: str = None, echo: bool = False):
        super().__init__(
            encryption_secret_key=encryption_secret_key
        )

        self.echo = echo

        self._mapper_registry = registry()
        self._metadata_obj = MetaData()
        self._scoped_session = None

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
            Column("deleted", Boolean, nullable=False),
            Column("enable_sharing_in_a_slack_channel", Boolean, nullable=False),
            Column("share_messages_in_slack_channel", String(256), nullable=True),
            Column("leaderbord_time_settings", Enum(LeaderbordTimeSettings), nullable=False),
            Column("enable_weekly_thank_you_limit", Boolean, nullable=False),
            Column("weekly_thank_you_limit", Integer, nullable=False),
            Column("receivers_number_limit", Integer, nullable=False),
            Column("enable_leaderboard", Boolean, nullable=False),
            Column("enable_private_message_counting_in_leaderboard", Boolean, nullable=False),
            Column("enable_company_values", Boolean, nullable=False),
            Column("enable_rich_text_in_thank_you_messages", Boolean, nullable=False),
            Column("enable_attaching_files", Boolean, nullable=False),
            Column("enable_private_messages", Boolean, nullable=False),
            Column("max_attached_files_num", Integer, nullable=False),
        )

        self._thank_you_types_table = Table(
            self._THANK_YOU_TYPES_TABLE,
            self._metadata_obj,
            Column("uuid", String(256), primary_key=True, nullable=False),
            Column("name", self.encrypted_string_column(256), nullable=False),
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
            Column("text", self.encrypted_text_column(), nullable=False),
            Column("is_rich_text", Boolean, nullable=False),
            Column("is_private", Boolean, nullable=False),
            Column("author_slack_user_id", String(256), nullable=False, index=True),
            Column("slash_command_slack_channel_id", String(256), nullable=True),
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
            Column("url", self.encrypted_string_column(1024), nullable=False),
            Column("filename", self.encrypted_string_column(512), nullable=False),
            Column("ordering_key", Integer, nullable=False),
        )

        self._employees_table = Table(
            self._EMPLOYEES_TABLE,
            self._metadata_obj,
            Column("uuid", String(256), primary_key=True, nullable=False),
            Column("company_uuid", String(256), ForeignKey(f"{self._COMPANIES_TABLE}.uuid"), nullable=False),
            Column("slack_user_id", String(256), nullable=False, index=True),
            Column("closed_welcome_message", Boolean, nullable=False),
            UniqueConstraint('company_uuid', 'slack_user_id', name='uix_employees__company__slack_user_id')
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
        self._mapper_registry.map_imperatively(Employee, self._employees_table)

        self._engine = self._create_engine()
        try:
            self._metadata_obj.create_all(bind=self._engine, checkfirst=True)
        except Exception as e:
            logging.error(f"Can not create database objects (tables / keys): {e}")
        self._session_maker = sessionmaker(bind=self._engine)
        self._session = self._session_maker()

    @property
    def session_maker(self):
        return self._session_maker

    def set_scoped_session(self, s_session: scoped_session):
        self._scoped_session = s_session

    @contextmanager
    def _get_session(self) -> Generator[Session, None, None]:
        """
        with self._session_maker() as session:
            yield session
            session.commit()
        """
        if self._scoped_session:
            try:
                session: Session = self._scoped_session()
                logging.debug(f"Successfully created/retrieved a session: {session}")
            except Exception as e:
                logging.debug(f"Can not create session using _flask_scoped_session: {e}")
                session = self._session
        else:
            session = self._session
        yield session
        session.commit()

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

    @classmethod
    def _read_thank_you_messages_sqlalchemy_result(cls, session: Session, company_uuid: str,
                                                   created_after: datetime = None, created_before: datetime = None,
                                                   with_types: List[str] = None, deleted: Optional[bool] = False,
                                                   private: Optional[bool] = None, author_slack_user_id: str = None,
                                                   receiver_slack_user_id: str = None, last_n: int = None):
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

        if private is not None:
            result = result.filter(ThankYouMessage.is_private == private)

        if author_slack_user_id is not None:
            result = result.filter(ThankYouMessage.author_slack_user_id == author_slack_user_id)

        # noinspection PyTypeChecker
        result = result.order_by(desc(ThankYouMessage.created_at))

        if last_n is not None:
            result = result.limit(last_n)

        return result.distinct()

    def read_thank_you_messages(self, company_uuid: str, created_after: datetime = None,
                                created_before: datetime = None, with_types: List[str] = None,
                                deleted: Optional[bool] = False, private: Optional[bool] = None,
                                author_slack_user_id: str = None, receiver_slack_user_id: str = None,
                                last_n: int = None) -> List[ThankYouMessage]:
        with self._get_session() as session:
            result = self._read_thank_you_messages_sqlalchemy_result(
                session=session,
                company_uuid=company_uuid,
                created_after=created_after,
                created_before=created_before,
                with_types=with_types,
                deleted=deleted,
                private=private,
                author_slack_user_id=author_slack_user_id,
                receiver_slack_user_id=receiver_slack_user_id,
                last_n=last_n
            )

            return result.all()

    def read_thank_you_messages_num(self, company_uuid: str, created_after: datetime = None,
                                    created_before: datetime = None, with_types: List[str] = None,
                                    deleted: Optional[bool] = False, private: Optional[bool] = None,
                                    author_slack_user_id: str = None, receiver_slack_user_id: str = None,
                                    last_n: int = None) -> int:
        with self._get_session() as session:
            result = self._read_thank_you_messages_sqlalchemy_result(
                session=session,
                company_uuid=company_uuid,
                created_after=created_after,
                created_before=created_before,
                with_types=with_types,
                deleted=deleted,
                private=private,
                author_slack_user_id=author_slack_user_id,
                receiver_slack_user_id=receiver_slack_user_id,
                last_n=last_n
            )

            return result.count()

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

    def read_companies(self, slack_team_id: str = None, deleted: Optional[bool] = False) \
            -> List[Company]:
        with self._get_session() as session:
            result = session.query(Company)
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
                                     leaders_num: int = 3, include_private: bool = False) \
            -> List[Tuple[Slack_User_ID_Type, int]]:
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

            if not include_private:
                result = result.filter(ThankYouMessage.is_private == false())

            result = result.group_by(ThankYouMessage.author_slack_user_id)
            result = result.order_by(func.count().desc())
            result = result.limit(leaders_num)

            return result.all()

    def get_thank_you_receiver_leaders(self, company_uuid: str, created_after: datetime = None,
                                       created_before: datetime = None, thank_you_type: ThankYouType = None,
                                       leaders_num: int = 3, include_private: bool = False) \
            -> List[Tuple[Slack_User_ID_Type, int]]:
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

            if not include_private:
                result = result.filter(ThankYouMessage.is_private == false())

            result = result.group_by(ThankYouReceiver.slack_user_id)
            result = result.order_by(func.count().desc())
            result = result.limit(leaders_num)

            return result.all()

    def create_employee(self, employee: Employee):
        self._set_obj(employee)

    def read_employee(self, company_uuid: UUID_Type, uuid: UUID_Type) -> Optional[Employee]:
        employee: Employee = self._get_obj(Employee, uuid)
        if employee and employee.company_uuid == company_uuid:
            return employee

    def read_employee_by_slack_id(self, company_uuid: UUID_Type, slack_user_id: Slack_User_ID_Type) \
            -> Optional[Employee]:
        with self._get_session() as session:
            result: List[Employee] = session.query(Employee).filter(Employee.slack_user_id == slack_user_id).all()
        if len(result) > 1:
            raise ValueError("There are multiple companies with the same slack_user_id value")
        try:
            return result[0]
        except IndexError:
            pass
