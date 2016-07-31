from datetime import datetime
import os
import numpy as np
import pandas as pd

from bcpp_export.communities import communities, intervention
from bcpp_export.constants import YES, NO
from django.conf import settings
from sqlalchemy import create_engine
from tabulate import tabulate

from bcpp_rdb.private_settings import Rdb

csv_options = dict(
    na_rep='',
    encoding='utf8',
    # date_format='%Y-%m-%d %H:%M:%S',
    index=True)


def to_date(value):
    s = str(value)
    return datetime(int(s[0:4]), int(s[4:6]), int(s[6:8]))


engine = create_engine('postgresql://{user}:{password}@{host}/{db}'.format(
    user=Rdb.user, password=Rdb.password, host=Rdb.host, db=Rdb.name))


df_subjects = pd.read_csv('/Users/erikvw/Documents/bcpp/nealia_subjects.csv', low_memory=False)

df_pims = pd.read_csv('/Users/erikvw/Documents/bcpp/nealia_pimspatient.csv')

# PIMS haart initiation
with engine.connect() as conn, conn.begin():
    df_haart = pd.read_sql_query('select * from dw.factpimshaartinitiation', conn)
df_haart = df_haart[df_haart['iscurrent'] == True]
df_haart['art_initiation_date'] = df_haart.apply(lambda row: to_date(row['initiationdatekey']), axis=1)
df_haart = df_haart.query('art_initiation_date <= datetime.today()')
df_haart.loc[:, 'pims_art_initiation_date'] = pd.to_datetime(df_haart['pims_art_initiation_date'])
df_haart = df_haart.query('dimcommonstudyparticipantkey != 0')

df_haart_sorted = df_haart.sort_values(['dimcommonstudyparticipantkey', 'art_initiation_date'])
df_haart_sorted.drop_duplicates('dimcommonstudyparticipantkey', keep='first', inplace=True)

# PIMS common study participant
df_common = pd.read_csv('/Users/erikvw/Documents/bcpp/dimcommonstudyparticipant.csv')
df_common = df_common[pd.notnull(df_common['bhssubjectid']) & pd.notnull(df_common['omangnumber']) & (df_common['omangnumber'] != 'unk') & (df_common['bhssubjectid'] != 'unk')]
df_common.rename(columns={'bhssubjectid': 'subject_identifier'}, inplace=True)


# merge PIMS haart fields on dimcommonstudyparticipantkey
df = pd.merge(df_haart_sorted[['dimcommonstudyparticipantkey', 'art_initiation_date']], df_common[['dimcommonstudyparticipantkey', 'subject_identifier']], how='left', on='dimcommonstudyparticipantkey')
df = df[pd.notnull(df['subject_identifier'])]

# merge
df_final = pd.merge(df_subjects, df, how='left', on='subject_identifier')
df_final = pd.merge(df_final, df_pims[['artcurrentpatientprogramstatusdescr', 'regdate', 'identity256']], how='left', on='identity256')
df_final.rename(columns={'regdate': 'pims_registration_date'}, inplace=True)
df_final.rename(columns={'artcurrentpatientprogramstatusdescr': 'pims_art_program_status'}, inplace=True)
df_final.rename(columns={'art_initiation_date': 'pims_art_initiation_date'}, inplace=True)
df_final['pims_registration_date'] = pd.to_datetime(df_final['pims_registration_date'])
df_final['pims_art_initiation_date'] = pd.to_datetime(df_final['pims_art_initiation_date'])
# df_final.to_csv('/Users/erikvw/Documents/bcpp/nealia_subjects_with_pims.csv', **options)

# add in HIVCareAdherence
# from bhp066.apps.bcpp_subject.models import HivCareAdherence
columns = ['subject_visit__household_member__registered_subject__subject_identifier',
           'subject_visit__household_member',
           'ever_taken_arv', 'on_arv', 'arv_evidence',
           'clinic_receiving_from', 'first_arv']
qs = HivCareAdherence.objects.values_list(*columns).all()
df_care = pd.DataFrame(list(qs), columns=columns)
df_care.rename(columns={'subject_visit__household_member__registered_subject__subject_identifier': 'subject_identifier'}, inplace=True)
df_care = df_care.sort_values(['subject_identifier', 'first_arv'], axis=0)
df_care.drop_duplicates('subject_identifier', keep='first', inplace=True)
df_care = df_care[pd.notnull(df_care['first_arv'])]
df_final = pd.merge(df_final, df_care[['subject_identifier', 'first_arv']], how='left', on='subject_identifier')
df_final['art_initiation_date'] = df_final.apply(lambda row: row['first_arv'] if pd.notnull(row['first_arv']) else row['pims_art_initiation_date'], axis=1)
df_final['pims_art_program_status'] = df_final.apply(lambda row: np.nan if row['pims_art_program_status'] == 'unk' else row['pims_art_program_status'], axis=1)
df_final.to_csv('/Users/erikvw/Documents/bcpp/nealia_subjects_with_pims3.csv', **csv_options)

# create group by tables
df1 = pd.DataFrame({'all': df_final.query('pair >= 1 and pair <= 11 and intervention == 1').query('final_hiv_status == 1 and (final_arv_status == 1 or final_arv_status == 2)').groupby('community').size()}).reset_index()
df1 = pd.merge(df1, pd.DataFrame({'init_date': df_final[pd.notnull(df_final['art_initiation_date'])].query('pair >= 1 and pair <= 11 and intervention == 1').query('final_hiv_status == 1 and (final_arv_status == 1 or final_arv_status == 2)').groupby('community').size()}).reset_index(), how='left', on='community')
print(tabulate(df1, headers=['community', 'naive_and_defaulters', 'init_dates'], tablefmt='psql'))

print(tabulate(df1, headers='i community all pos on_arv naive reg on_arv_reg naive_reg on_arv_reg% naive_reg%'.split(' '), tablefmt='psql'))
