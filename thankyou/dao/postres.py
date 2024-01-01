from sqlalchemy import Engine, create_engine

from thankyou.dao.sqlalchemy import SQLAlchemyDao


class PostgresDao(SQLAlchemyDao):
    def __init__(self, host: str, database: str, user: str, password: str, port: int = 5432):
        self.conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        super().__init__()

    def _create_engine(self) -> Engine:
        return create_engine(self.conn_string)
