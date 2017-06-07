import os
import pandas as pd


# import csv
# from bcpp_rdb.identity256 import identity256
# from edc_registration.models import RegisteredSubject
#
# values = ((obj.subject_identifier, obj.identity) for obj in RegisteredSubject.objects.all())
#
# with open('/home/django/bcpp_subjects.csv', 'w') as f:
#     writer = csv.writer(f)
#     for value in values:
#         writer.writerow(value)
#
# df_subject_identifiers['identity256'] = df_subject_identifiers.apply(
#     lambda row: identity256(row, column_name='identity'), axis=1)


# files
path = '/Users/erikvw/Documents/bcpp/pims/20170607/'
bcpp_subjects_file = os.path.join(
    path, 'bcpp_subjects_2017-06-07-1529444004640200.csv')
bcpp_subject_identifiers_file = os.path.join(
    path, 'bcpp_subjects_identifiers_2017-06-07.csv')
seroconverters_file = os.path.join(
    path, 'seroconverters01JUN17.csv')
pims_file = os.path.join(path, 'pims_haart_2017-06-07-1326116452540200.csv')
htc_file = os.path.join(path, 'htc_2017-06-07-1327252560230200.csv')
export_file = os.path.join(
    path, 'seroconverters01JUN17_with_pims.csv')

# dataframes
df_subjects = pd.read_csv(bcpp_subjects_file, encoding='utf-8')
df_subjects.sort_values(
    ['subject_identifier', 'consent_datetime'], inplace=True)
df_subjects.drop_duplicates(['subject_identifier'], keep='first', inplace=True)

df_subject_identifiers = pd.read_csv(
    bcpp_subject_identifiers_file, encoding='utf-8')

df_sero = pd.read_csv(seroconverters_file, encoding='utf-8')
df_pims = pd.read_csv(pims_file, encoding='utf-8')
df_pims = df_pims[df_pims['identity_type'] == 'Omang']
df_htc = pd.read_csv(htc_file, encoding='utf-8')
df_htc['identity256'] = df_htc['omang_nbr']

# merged dataframes
df_subjects = pd.merge(df_subjects, df_subject_identifiers, how='left',
                       on='subject_identifier', suffixes=['', '_erik'])

df = pd.merge(df_sero, df_subjects, how='left',
              on='subject_identifier', suffixes=['', '_erik'])
df1 = pd.merge(df, df_pims, how='left',
               on='identity256', suffixes=['', '_pims'])
df1.drop_duplicates(inplace=True)
df2 = pd.merge(df1, df_htc, how='left',
               on='identity256', suffixes=['', '_htc'])
