import sys

from sqlalchemy import Engine, create_engine

from thankyou.dao.sqlalchemy import SQLAlchemyDao


class PostgresDao(SQLAlchemyDao):
    CONN_PYTEST_STRING = "postgresql://localhost:5432/thank_you_test"
    CONN_STRING = "postgresql://localhost:5432/thank_you"

    def _create_engine(self) -> Engine:
        conn_string = self.CONN_STRING if "pytest" not in sys.modules else self.CONN_PYTEST_STRING
        print(conn_string)
        return create_engine(conn_string)
