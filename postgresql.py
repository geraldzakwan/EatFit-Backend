import os
import sqlalchemy

from dotenv import load_dotenv, find_dotenv
from sqlalchemy import or_, func

load_dotenv(find_dotenv(), override=True)


class PostgreSQL:
    def __init__(self):
        self.con, self.meta = self._connect()

    @staticmethod
    def _connect():
        url = os.environ['DATABASE_URL']
        con = sqlalchemy.create_engine(url, client_encoding='utf8')
        meta = sqlalchemy.MetaData(bind=con, reflect=True)

        return con, meta
