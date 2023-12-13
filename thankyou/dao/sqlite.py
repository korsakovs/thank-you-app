import os
import sys

from sqlalchemy import Engine, create_engine, NullPool

from thankyou.dao.sqlalchemy import SQLAlchemyDao


class SQLiteDao(SQLAlchemyDao):
    _DB_FILENAME = "update_me.db"
    _DB_PYTEST_FILENAME = "pytest_update_me.db"

    @property
    def _db_folder(self):
        return os.path.join(os.path.dirname(__file__), "..", "..", "db")

    @property
    def _db_file(self):
        filename = self._DB_FILENAME if "pytest" not in sys.modules else self._DB_PYTEST_FILENAME
        return os.path.join(self._db_folder, filename)

    def _create_engine(self) -> Engine:
        if not os.path.isdir(self._db_folder):
            os.mkdir(self._db_folder)
        return create_engine(f"sqlite:///{self._db_file}", echo=False, poolclass=NullPool)
