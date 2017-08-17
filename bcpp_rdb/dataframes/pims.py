import numpy as np
import os
import pandas as pd

from datetime import datetime
from sqlalchemy import create_engine

from ..private_settings import Rdb

# Rdb.host = '127.0.0.1:5000'


class Pims(object):

    def __init__(self, path=None, timeout=None, host=None, port=None):
        self._df_pims = pd.DataFrame()
        self.path = path or os.path.expanduser('~/Documents/bcpp/pims/')
        if timeout:
            connect_args = {'connect_timeout': timeout}
        else:
            connect_args = {}
        self.engine = create_engine('postgresql://{user}:{password}@{host}:{port}/{db}'.format(
            user=Rdb.user, password=Rdb.password, host=host or Rdb.host, db=Rdb.name, port=port or Rdb.port),
            connect_args=connect_args)

    def update_pg_tables(self):
        for name in self.pg_table_names:
            self.pg_table_to_csv(name)

    @property
    def pg_table_names(self):
        return [
            #'dimcommonstudyparticipant',
            #'dimcurrentpimspatient',
            #'dimpimsappointmentvisit',
            'factpimshivtest',
            #'factpimsartpatientregistration',
            #'factpimshaarteligibility',
            #'factpimshaartinitiation',
            #'factpimshaartreinitiation',
        ]

    def pg_table_to_csv(self, name):
        with self.engine.connect() as conn, conn.begin():
            df = pd.read_sql_query('select * from dw.{}'.format(name), conn)
        df.to_csv(os.path.expanduser('~/{}.csv'.format(name)), index=False)
        return df

    def load_pg_table_from_csv(self, pg_table_name, csv_filename=None):
        filename = csv_filename or os.path.join(
            self.path, '{}.csv'.format(pg_table_name))
        df = pd.read_csv(
            os.path.join(self.path, filename),
            low_memory=False)
        return df

    @property
    def df_pims_patient(self):
        """Loads the dimcurrentpimspatient table from CSV, removes duplicates,
        and filters for citizens between 16-64 years old."""
        if self._df_pims.empty:
            df = pd.read_csv(
                os.path.expanduser(
                    '/Users/erikvw/Documents/bcpp/dimcurrentpimspatient.csv'),
                low_memory=False)
            df.rename(columns={'idno': 'identity256'}, inplace=True)
            # calculate age
            df['dob'] = pd.to_datetime(df['dob'], format='%Y-%m-%d %H:%M:%S')
            df['age'] = (datetime.today() - df['dob']).astype('<m8[Y]')
            # remove temporary identifiers allocated at the clinic before dedup
            df['identity256'] = df.apply(
                lambda row: np.nan if row['idtype'] == 'Temporary ID' else row['identity256'], axis=1)
            df['identity256'] = df.apply(
                lambda row: np.nan if row['identity256'] == 'unk' else row['identity256'], axis=1)
            # sort on identity and registration date
            df = df[pd.notnull(df['regdate'])].sort_values(
                ['identity256', 'regdate'], ascending=[True, True])
            # remove dups
            df = df.drop_duplicates('identity256', keep='first')
            df = df[(df['citizenship'].isin(['Citizen', 'Spouse of citizen'])) &
                    (df['age'] >= 16) &
                    (df['age'] <= 64) &
                    (pd.notnull(df['dob']))]
            self._df_pims = df
        return self._df_pims
