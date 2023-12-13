from thankyou.core.config import get_active_dao_type, DaoType, INITIAL_THANK_YOU_TYPES
from thankyou.core.models import Company, ThankYouType
from thankyou.dao.postres import PostgresDao
from thankyou.dao.sqlite import SQLiteDao

if get_active_dao_type() == DaoType.POSTGRES:
    dao = PostgresDao()
elif get_active_dao_type() == DaoType.SQLITE:
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
            new_thank_you_type = ThankYouType(name=name, company=company)
            dao.create_thank_you_type(new_thank_you_type)
            existing_thank_you_types.append(new_thank_you_type)
