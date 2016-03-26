import os
import numpy as np
import pandas as pd

from bcpp_export.communities import communities, intervention
from bcpp_export.constants import YES, NO
from django.conf import settings
from sqlalchemy import create_engine
from tabulate import tabulate

from .private_settings import Rdb

yes_no = {'Yes': YES, 'No': NO, None: np.nan}


class Htc(object):

    def __init__(self, path=None, csv_filename=None, pg_load=None, timeout=None):
        self._df_baseline = pd.DataFrame()
        self._df_summary = pd.DataFrame()
        self.path = path or os.path.join(os.path.expanduser('~/Documents/bcpp/'), csv_filename or 'htc.csv')
        self.engine = create_engine('postgresql://{user}:{password}@{host}/{db}'.format(
            user=Rdb.user, password=Rdb.password, host=Rdb.host, db=Rdb.name),
            connect_args={'connect_timeout': timeout or 60})
        if pg_load:
            self.results = self.pg_load()
        else:
            self.results = self.csv_load()

    def df_baseline(self):
        """Return a dataframe after removing duplicates by OMANG, keeping first in date order."""
        if self._df_baseline.empty:
            results = self.results.sort_values('final_hiv_status_date')
            results.drop_duplicates('identity256', keep='first', inplace=True)
        return self._df_baseline

    @property
    def df_targets(self):
        return pd.read_csv(os.path.join(settings.BASE_DIR, 'csv', 'htc_estimates.csv'))

    @property
    def df_summary(self):
        if self._df_summary.empty:
            query = (
                'age >= 16 and age <= 64 and '
                'final_hiv_status == 1 and '
                'citizenship == \'Citizen\' and '
                'perm_resident == \'Yes\' and '
                'identity_type == \'OMANG\'')
            df_summary = self.df_baseline.query(query)[pd.notnull(self.df_baseline['identity256'])].groupby(
                ['pair', 'community']).size().reset_index(name='htc')
            df_summary = pd.merge(
                df_summary, self.df_targets, how="left", on="pair", suffixes=('', '_y'))
            df_summary.drop('community_y', axis=1, inplace=True)
            df_summary['%htc_target'] = 100 * df_summary['htc'] / df_summary['htc_target']
            df_summary = df_summary.round({'%htc_target': 0})
            self._df_summary = df_summary
        return self._df_summary

    def print_summary(self):
        print tabulate(
            self.df_summary,
            headers=['pair', 'community', 'htc', 'htc_target', '%htc_target'],
            tablefmt='psql')

    def csv_load(self):
        return pd.read_csv(self.path)

    def pg_load(self):
        with self.engine.connect() as conn, conn.begin():
            df = pd.read_sql_query(self.pg_sql_query, conn)
        df = df.rename(columns={
            'rdbcalculatedage': 'age',
            'citizen_ind': 'citizenship',
            'community_name': 'community',
            'prior_hiv_test_result': 'recorded_result',
            'self_report_hiv_test_result': 'verbal_hiv_result',
            'hiv_test_result': 'today_hiv_result',
            'interview_date': 'final_hiv_status_date'})
        df['community'] = df.apply(lambda row: row['community'].lower().replace(' ', '_'), axis=1)
        df['community'] = df.apply(
            lambda row: 'lentsweletau' if row['community'] == 'lentswelatau' else row['community'], axis=1)
        df['gender'] = df['gender'].map({'Male': 1, 'Female': 2, None: np.nan}.get)
        df['citizenship'] = df['citizenship'].map({'Yes': 'Citizen', 'No': 'Non-citizen'}.get)
        df['has_omang'] = df['has_omang'].map({'Yes': YES, 'No': NO, None: np.nan}.get)
        df['identity256'] = df.apply(
            lambda row: row['omang_nbr'] if pd.notnull(row['omang_nbr']) and row['has_omang'] == YES else np.nan,
            axis=1)
        df['identity_type'] = df.apply(
            lambda row: 'OMANG' if row['has_omang'] == YES else np.nan, axis=1)
        df['final_hiv_status'] = df.apply(
            lambda row: self.final_hiv_status(row), axis=1)
        df['final_hiv_status_source'] = df.apply(
            lambda row: self.final_hiv_status_source(row), axis=1)
        df['raw_hiv_status_sequence'] = df.apply(
            lambda row: self.raw_hiv_status(row), axis=1)
        df['final_hiv_status'] = df['final_hiv_status'].map({'HIV+': 1, 'HIV-': 0}.get)
        df.drop(['recorded_result', 'verbal_hiv_result', 'today_hiv_result', 'has_omang', 'omang_nbr'],
                axis=1, inplace=True)
        df['intervention'] = df.apply(lambda row: intervention(row), axis=1)
        df['pair'] = df.apply(lambda row: communities.get(row['community']).pair, axis=1)
        df = df[df['intervention'] == 1]
        df.to_csv(
            path_or_buf=self.path, na_rep='', encoding='utf8', date_format='%Y-%m-%d %H:%M:%S', index=True)
        return df

    @property
    def pg_sql_query(self):
        path = os.path.join(settings.BASE_DIR, 'sql', 'htc.sql')
        with open(path, 'r') as f:
            sql = f.read()
        return sql

    def final_hiv_status(self, row):
        if pd.notnull(row.today_hiv_result):
            return row.today_hiv_result
        elif pd.notnull(row.recorded_result):
            return row.recorded_result
        elif pd.notnull(row.verbal_hiv_result):
            return row.verbal_hiv_result
        else:
            return np.nan

    def final_hiv_status_source(self, row):
        if pd.notnull(row.today_hiv_result):
            return 'today_hiv_result'
        elif pd.notnull(row.recorded_result):
            return 'recorded_result'
        elif pd.notnull(row.verbal_hiv_result):
            return 'verbal_hiv_result'
        else:
            return np.nan

    def raw_hiv_status(self, row):
        raw_hiv_status = []
        if pd.notnull(row.verbal_hiv_result):
            raw_hiv_status.append(row.verbal_hiv_result)
        if pd.notnull(row.recorded_result):
            raw_hiv_status.append(row.recorded_result)
        if pd.notnull(row.today_hiv_result):
            raw_hiv_status.append(row.today_hiv_result)
        if not raw_hiv_status:
            return np.nan
        else:
            return ','.join(raw_hiv_status)
