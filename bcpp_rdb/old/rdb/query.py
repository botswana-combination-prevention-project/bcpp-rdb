import os
import pandas as pd

from datetime import datetime
from bcpp_rdb.private_settings import Rdb
from sqlalchemy import create_engine

engine = create_engine('postgresql://{user}:{password}@{host}/{db}'.format(
    user=Rdb.user, password=Rdb.password, host=Rdb.host, db=Rdb.name))


class Pims(object):

    def __init__(self):
        self._df_pims = pd.DataFrame()

    def tables(self):
        return [
            'dimcommonstudyparticipant',
            'dimcurrentpimspatient',
            'dimpimsappointmentvisit'
            'factpimshivtest',
            'factpimshaartinitiation',
        ]

    def import_pg_table(self, name):
        with engine.connect() as conn, conn.begin():
            df = pd.read_sql_query('select * from dw.{}'.format(name), conn)
        df.to_csv(os.path.expanduser('~/{}.csv'.format(name)))

    def df_pims(self):
        if self._df_pims.empty:
            df = pd.read_csv(
                os.path.expanduser('/Users/erikvw/Documents/bcpp/dimcurrentpimspatient.csv'),
                low_memory=False)
            df['age'] = (datetime.today() - df['dob']).astype('<m8[Y]')
            df = df.sort_values(['idno', 'regdate'], ascending=[True, False])
            df = df.drop_duplicates('idno')
            df = df[(df['citizenship'].isin(['Citizen', 'Spouse of citizen'])) &
                    (df['age'] >= 16) &
                    (df['age'] <= 64) &
                    (pd.notnull(df['dob']))]
            self._df_pims = df
        return self._df_pims
