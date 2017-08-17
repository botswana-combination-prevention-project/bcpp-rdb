import re

import pandas as pd
import numpy as np

from edc_pdutils import identity256

pattern = r'^[0-9]{4}[12]{1}[0-9]{4}$'
options = dict(na_rep='', encoding='utf8', index=True)


def vl_bcpp(result, quantifier):
    vl_bcpp = np.nan
    if pd.notnull(result):
        if (result <= 400 and quantifier == '<'):
            vl_bcpp = '<   400'
        elif (result < 10000 and quantifier in ['=', '>']):
            vl_bcpp = '< 10000'
        elif (result >= 10000 and quantifier in ['=', '>']):
            vl_bcpp = '>=10000'
    return vl_bcpp


def vl_result(value):
    pattern = r'[0-9]\d+'
    vl_result = np.nan
    if pd.notnull(value):
        search = re.search(pattern, value)
        if search:
            vl_result = int(search.group())
    return vl_result


def vl_quantifier(value):
    pattern = r'[\<\>]{1}'
    vl_quantifier = np.nan
    if pd.notnull(vl_result(value)):
        vl_quantifier = '='
        search = re.search(pattern, value)
        if search:
            vl_quantifier = search.group()
    return vl_quantifier


def cd4_result(value):
    if pd.notnull(value) and not re.match('[A-Za-z]', value):
        cd4_result = int(round(float(value.strip()), 0))
    else:
        cd4_result = np.nan
    return cd4_result


def cd4_bcpp(cd4_result):
    cd4_bcpp = np.nan
    if pd.notnull(cd4_result):
        cd4_result = int(round(float(cd4_result), 0))
        if cd4_result < 500:
            cd4_bcpp = 'LO'
        elif cd4_result >= 500:
            cd4_bcpp = 'HI'
    return cd4_bcpp


# demographics
ipms_demo = pd.read_csv(
    '/Users/erikvw/Documents/bcpp/IPMS_BCPP_Variables-demographics.csv')
ipms_demo['identity'] = ipms_demo.apply(lambda row: np.nan if pd.isnull(row['UniquePublicIdentifier']) else str(
    row['UniquePublicIdentifier']).strip().replace('-', '').replace('_', ''), axis=1)
ipms_demo['art_initiation_date'] = pd.to_datetime(ipms_demo['ART_INIT_DATE'])
ipms_demo['valid_identity'] = ipms_demo[pd.notnull(
    ipms_demo['identity'])]['identity'].str.match(pattern)
ipms_demo['identity256'] = ipms_demo[ipms_demo['valid_identity'] ==
                                     True].apply(lambda row: identity256(row, 'identity'), axis=1)

# lab results
ipms_lab = pd.read_csv(
    '/Users/erikvw/Documents/bcpp/IPMS_BCPP_Variables-lab.csv')
ipms_lab['vl_result'] = ipms_lab.apply(
    lambda row: vl_result(row['VL_Result']), axis=1)
ipms_lab['vl_quantifier'] = ipms_lab.apply(
    lambda row: vl_quantifier(row['VL_Result']), axis=1)
ipms_lab['vl_bcpp'] = ipms_lab.apply(lambda row: vl_bcpp(
    row['vl_result'], row['vl_quantifier']), axis=1)
ipms_lab['vl_datetime'] = pd.to_datetime(ipms_lab['VL_Date'])
ipms_lab['cd4_datetime'] = pd.to_datetime(ipms_lab['CD4_Date'])
ipms_lab['cd4_result'] = ipms_lab.apply(
    lambda row: cd4_result(row['CD4_Result']), axis=1)
ipms_lab['cd4_bcpp'] = ipms_lab.apply(
    lambda row: cd4_bcpp(row['cd4_result']), axis=1)

# visits
ipms_visits = pd.read_csv(
    '/Users/erikvw/Documents/bcpp/IPMS_BCPP_Variables-clinic.csv', low_memory=False)
ipms_visits.loc[:, 'visit_datetime'] = pd.to_datetime(ipms_visits['VisitDate'])

# merge
ipms = pd.merge(ipms_demo, ipms_lab, on='PatientID', how='left')
ipms = pd.merge(ipms, ipms_visits[[
                'PatientID', 'VisitID', 'visit_datetime']], on='PatientID', how='left')
ipms.sort_values(['PatientID', 'visit_datetime'], inplace=True)

# flag dups
ipms['dup_vl'] = ipms.duplicated(
    ['vl_datetime', 'identity256', 'vl_result', 'vl_quantifier'])
ipms['dup_cd4'] = ipms.duplicated(
    ['cd4_datetime', 'identity256', 'cd4_result'])
ipms['dup'] = ipms.duplicated(
    ['vl_datetime', 'cd4_datetime', 'identity256', 'cd4_result', 'vl_result'])

# to csv
ipms.to_csv('/Users/erikvw/Documents/bcpp/nealia_ipms.csv', **options)

ipms = pd.read_csv(
    '/Users/erikvw/Documents/bcpp/nealia_ipms.csv', low_memory=False)

df_subjects = pd.read_csv(
    '/Users/erikvw/Documents/bcpp/nealia_subjects_with_pims6.csv', low_memory=False)

df = pd.merge(df_subjects, ipms.query('dup == False')[
              ['vl_datetime', 'LocationName', 'identity256', 'VL_Result']], how='left', on='identity256')
