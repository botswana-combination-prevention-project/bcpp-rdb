import os
import pytz

from datetime import datetime
from django.conf import settings

from ..mixins import DataframeMixin, get_statinfo

tz = pytz.timezone(settings.TIME_ZONE)


class QueryMixin(DataframeMixin):

    csv_path = settings.UPLOAD_FOLDER

    def fetch_from_db(self, name):
        dataframe = self.get_dataframe(**self.query_parameters(name))
        dataframe = self.update_dataframe(name, dataframe)
        fname = self.csv_filename(name)
        dataframe.to_csv(os.path.join(self.csv_path, fname), index=False)
        statinfo = get_statinfo(self.csv_path, fname)
        return statinfo

    def update_dataframe(self, name, dataframe):
        return dataframe

    def csv_filename(self, filename_prefix):
        timestamp = tz.localize(
            datetime.today()).isoformat(sep='-').replace('.', '').replace(':', '').replace('+', '')
        return f'{filename_prefix}_{timestamp}.csv'

    def query_parameters(self, name):
        """Return a dict with connection_name and sql.
        """
        if name == 'pims_haart':
            with open(os.path.join(settings.STATIC_ROOT, 'bcpp_rdb', 'sql', 'pims_haart.sql'), 'r') as f:
                query_parameters = {'sql': f.read(), 'connection_name': 'rdb'}
        elif name == 'pims':
            with open(os.path.join(settings.STATIC_ROOT, 'bcpp_rdb', 'sql', 'pims.sql'), 'r') as f:
                query_parameters = {'sql': f.read(), 'connection_name': 'rdb'}
        elif name == 'htc':
            with open(os.path.join(settings.STATIC_ROOT, 'bcpp_rdb', 'sql', 'htc.sql'), 'r') as f:
                query_parameters = {'sql': f.read(), 'connection_name': 'rdb'}
        elif name == 'bcpp_subjects':
            with open(os.path.join(settings.STATIC_ROOT, 'bcpp_rdb', 'sql', 'bcpp_subjects.sql'), 'r') as f:
                query_parameters = {'sql': f.read(), 'connection_name': 'bcpp'}
        elif name == 'bcpp_requisitions':
            with open(os.path.join(settings.STATIC_ROOT, 'bcpp_rdb', 'sql', 'bcpp_requisitions.sql'), 'r') as f:
                query_parameters = {'sql': f.read(), 'connection_name': 'bcpp'}
        elif name == 'bcpp_test':
            with open(os.path.join(settings.STATIC_ROOT, 'bcpp_rdb', 'sql', 'bcpp_test.sql'), 'r') as f:
                query_parameters = {'sql': f.read(), 'connection_name': 'bcpp'}
        elif name == 'rdb_test':
            with open(os.path.join(settings.STATIC_ROOT, 'bcpp_rdb', 'sql', 'rdb_test.sql'), 'r') as f:
                query_parameters = {'sql': f.read(), 'connection_name': 'rdb'}
        return query_parameters
