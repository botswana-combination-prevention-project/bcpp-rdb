import os
import pandas as pd

from bcpp_rdb.mixins import RdbConnectionMixin

# Rdb.host = '127.0.0.1:5000'


class Pims(RdbConnectionMixin):

    def __init__(self, path=None, timeout=None, host=None, port=None):
        self._df_pims = pd.DataFrame()
        self.path = path or os.path.expanduser('~/Documents/bcpp/pims/')

    @property
    def sql(self):
        return ('SELECT idno as identity256, idtype as identity_type, regdate as pims_registration_date, '
                'initiationdatekey as pims_art_initiation_date, p.pimsclinicname, '
                'artcurrentpatientprogramstatusdescr '
                'FROM dw.factpimshaartinitiation i '
                'JOIN dw.dimpimspatient p ON i.dimpimspatientkey=p.dimpimspatientkey '
                'WHERE i.iscurrent=True')

    def query_to_csv(self, name):
        with self.engine.connect() as conn, conn.begin():
            df = pd.read_sql_query(self.sql, conn)
        df.to_csv(os.path.expanduser('~/{}.csv'.format(name)), index=False)
        return df
