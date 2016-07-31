import os
import pandas as pd
import numpy as np
from dateutil.parser import parse

# files
path = '/Users/erikvw/Documents/bcpp/bcpp_interview/'
bcpp_subjects_file = os.path.join(path, 'bcpp_subjects_2016-07-31-122804.524479+0200.csv')
nealia_file = os.path.join(path, 'Qualitative Sub Study Subject List 28JUL2016.csv')
pims_file = os.path.join(path, 'pims_haart_2016-07-31-003048.336415+0200.csv')
htc_file = os.path.join(path, 'htc_2016-07-31-002100.350170+0200.csv')
export_file = os.path.join(path, 'Qualitative Sub Study Subject List 28JUL2016-with_pims.csv')

# dataframes
df_subjects = pd.read_csv(bcpp_subjects_file)
df_subjects.sort_values(['subject_identifier', 'consent_datetime'], inplace=True)
df_subjects.drop_duplicates(['subject_identifier'], keep='first', inplace=True)
df_nealia = pd.read_csv(nealia_file)
df_pims = pd.read_csv(pims_file)
df_pims = df_pims[df_pims['identity_type'] == 'Omang']
df_htc = pd.read_csv(htc_file)
df_htc['identity256'] = df_htc['omang_nbr']

# merged dataframes
df = pd.merge(df_nealia, df_subjects, how='left', on='subject_identifier', suffixes=['', '_erik'])
df1 = pd.merge(df, df_pims, how='left', on='identity256', suffixes=['', '_pims'])
df1.drop_duplicates(inplace=True)
df2 = pd.merge(df1, df_htc, how='left', on='identity256', suffixes=['', '_htc'])

# clean up before export
df2['pims_art_initiation_date'] = df2.apply(
    lambda row: (row['pims_art_initiation_date']
                 if pd.isnull(row['pims_art_initiation_date'])
                 else parse(str(int(row['pims_art_initiation_date'])))), axis=1)
date_columns = ['T1_visit_date', 'consent_date', 'dob', 'consent_datetime', 'pims_registration_date', 'interview_date']
for column in date_columns:
    df2[column] = df2.apply(
        lambda row: row[column] if pd.isnull(row[column]) else parse(row[column]), axis=1)

for column in list(df2.select_dtypes(include=['datetime64[ns, UTC]']).columns):
    df2[column] = df2[column].astype('datetime64[ns]')
df2.fillna(value=np.nan, inplace=True)
df2.replace('', np.nan, inplace=True)


# export
df2.to_csv(export_file, index=False)
