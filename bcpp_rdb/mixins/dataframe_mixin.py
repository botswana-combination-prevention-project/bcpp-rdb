import pytz
import pandas as pd

from django.conf import settings
from sqlalchemy.engine import create_engine

from ..private_settings import Rdb, Edc

tz = pytz.timezone(settings.TIME_ZONE)


class DataframeMixin:

    conn_settings = Rdb, Edc

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        string = None
        self.engine = {}
        self.db_connections = {}
        for settings in self.conn_settings:
            if settings.engine == 'pg':
                string = 'postgresql://{user}:{password}@{host}:{port}/{dbname}'
            elif settings.engine == 'mysql':
                string = 'mysql+mysqldb://{user}:{password}@{host}:{port}/{dbname}'
            string = string.format(
                user=settings.user,
                password=settings.password,
                host=settings.host,
                dbname=settings.dbname,
                port=settings.port)
            self.engine[settings.connection_name] = self.open_engine(string)
            self.db_connections[settings.connection_name] = dict(
                name=settings.connection_name,
                host=settings.host,
                dbname=settings.dbname,
                port=settings.port)

    def open_engine(self, string):
        connect_args = {}
        try:
            if settings.timeout:
                connect_args = {'connect_timeout': settings.timeout}
            else:
                connect_args = {}
        except AttributeError:
            pass
        return create_engine(string, connect_args=connect_args)

    def get_dataframe(self, sql=None, connection_name=None):
        """Return a dataframe for the sql query."""
        with self.engine[connection_name].connect() as conn, conn.begin():
            dataframe = pd.read_sql_query(sql, conn)
        return dataframe
