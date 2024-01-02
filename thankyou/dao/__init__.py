import logging
import os
from threading import Lock

from thankyou.core.config import get_active_dao_type, DaoType, INITIAL_THANK_YOU_TYPES
from thankyou.core.models import Company, ThankYouType
from thankyou.dao.postres import PostgresDao
from thankyou.dao.sqlite import SQLiteDao


__CREATE_DAO_LOCK = Lock()


with __CREATE_DAO_LOCK:
    if get_active_dao_type() == DaoType.POSTGRES:
        logging.info("USING POSTGRES DAO")
        postgres_host = os.getenv("POSTGRES_HOST")
        postgres_port = int(os.getenv("POSTGRES_PORT") or "5432")
        postgres_user = os.getenv("SLACK_APP_POSTGRES_USERNAME")
        postgres_password = os.getenv("SLACK_APP_POSTGRES_PASSWORD")
        postgres_db = os.getenv("POSTGRES_DB")
        dao = PostgresDao(
            database=postgres_db,
            host=postgres_host,
            port=postgres_port,
            user=postgres_user,
            password=postgres_password
        )
    elif get_active_dao_type() == DaoType.SQLITE:
        logging.info("USING SQLITE DAO")
        dao = SQLiteDao()
    else:
        raise TypeError(f"DAO {get_active_dao_type().name} is not supported")


def create_initial_data(company: Company):
    existing_thank_you_types = dao.read_thank_you_types(company_uuid=company.uuid)
    for name in INITIAL_THANK_YOU_TYPES:
        for thank_you_type_ in existing_thank_you_types:
            if thank_you_type_.name == name:
                break
        else:
            new_thank_you_type = ThankYouType(name=name, company_uuid=company.uuid)
            dao.create_thank_you_type(new_thank_you_type)
            existing_thank_you_types.append(new_thank_you_type)
