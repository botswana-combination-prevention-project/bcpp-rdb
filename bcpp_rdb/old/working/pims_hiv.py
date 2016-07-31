import pandas as pd

from sqlalchemy import create_engine
from bcpp_rdb.private_settings import Rdb
from tabulate import tabulate

engine = create_engine('postgresql://{user}:{password}@{host}/{db}'.format(
    user=Rdb.user, password=Rdb.password, host=Rdb.host, db=Rdb.name))

options = dict(na_rep='',
               encoding='utf8',
               index=True)

df_pims = pd.read_csv('/Users/erikvw/Documents/bcpp/nealia_pimspatient.csv')

sql = 'select * from dw.factpimshivtest'
with engine.connect() as conn, conn.begin():
    df_hiv = pd.read_sql_query(sql, conn)

# d_hiv.to_csv('/Users/erikvw/Documents/bcpp/pims_factpimshivtest.csv', **options)

y = pd.merge(
    df_pims, df_hiv.query('iscurrent==True')[
        ['dimcurrentpimspatientkey', 'labtest', 'labtestresult', 'labresultclassoption']],
    how='left', on=u'dimcurrentpimspatientkey')

y.groupby('labresultclassoption').size()

y['result'] = y.apply(
    lambda row: row['labresultclassoption'] if row['labresultclassoption'] else ['labtestresult'],
    axis=1)
y.groupby('result').count()
print(tabulate(pd.DataFrame({'count': y.groupby('result').size()}).reset_index(),
               headers=['Result', 'Count'], tablefmt='psql'))
