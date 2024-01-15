from sqlalchemy import Engine, create_engine

from thankyou.core.config import get_env, Env
from thankyou.dao.sqlalchemy import SQLAlchemyDao


class PostgresDao(SQLAlchemyDao):
    def __init__(self, host: str, database: str, user: str, password: str, port: int = 5432,
                 encryption_secret_key: str = None, echo: bool = False):
        self.conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        super().__init__(encryption_secret_key=encryption_secret_key, echo=echo)

    def _create_engine(self) -> Engine:
        return create_engine(self.conn_string, echo=self.echo, pool_recycle=3600, pool_timeout=20)
