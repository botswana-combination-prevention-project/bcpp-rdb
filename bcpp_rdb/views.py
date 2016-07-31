import copy
import json
import os
import pytz

from datetime import datetime
from django.conf import settings
from django.views.generic.base import TemplateView

from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin

from .mixins import FileItemsMixin, AsyncMixin, DataframeMixin, get_statinfo
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

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
        return '{}_{}.csv'.format(
            filename_prefix, tz.localize(
                datetime.today()).isoformat(sep='-').replace('.', '').replace(':', '').replace('+', ''))

    def query_parameters(self, name):
        """Return a dict with connection_name and sql."""
        if name == 'pims_haart':
            with open(os.path.join(settings.STATIC_ROOT, 'bcpp_rdb', 'sql', 'pims_haart.sql'), 'r') as f:
                query_parameters = {'sql': f.read(), 'connection_name': 'rdb'}
        elif name == 'htc':
            with open(os.path.join(settings.STATIC_ROOT, 'bcpp_rdb', 'sql', 'htc.sql'), 'r') as f:
                query_parameters = {'sql': f.read(), 'connection_name': 'rdb'}
        elif name == 'bcpp_subjects':
            with open(os.path.join(settings.STATIC_ROOT, 'bcpp_rdb', 'sql', 'bcpp_subjects.sql'), 'r') as f:
                query_parameters = {'sql': f.read(), 'connection_name': 'bcpp'}
        elif name == 'bcpp_test':
            with open(os.path.join(settings.STATIC_ROOT, 'bcpp_rdb', 'sql', 'bcpp_test.sql'), 'r') as f:
                query_parameters = {'sql': f.read(), 'connection_name': 'bcpp'}
        elif name == 'rdb_test':
            with open(os.path.join(settings.STATIC_ROOT, 'bcpp_rdb', 'sql', 'rdb_test.sql'), 'r') as f:
                query_parameters = {'sql': f.read(), 'connection_name': 'rdb'}
        return query_parameters


class HomeView(EdcBaseViewMixin, FileItemsMixin, AsyncMixin, QueryMixin, TemplateView):

    template_name = 'bcpp_rdb/home.html'
    response_data = {}

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EdcBaseViewMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        self.add_file_item('pims_haart', 'PIMS Haart data')
        self.add_file_item('htc', 'HTC data')
        self.add_file_item('bcpp_subjects', 'BCPP Subjects')
        self.add_test_file_item('bcpp_test', 'BCPP Test')
        self.add_test_file_item('rdb_test', 'RDB Test')
        self.add_static_file_item('bcpp_rdb_key', 'BCPP/RDB Subject Key')
        context = super().get_context_data(**kwargs)
        context.update({
            'file_items': self.file_items,
            'test_file_items': self.test_file_items,
            'static_file_items': self.static_file_items,
            'upload_url': settings.UPLOAD_URL,
            'connections': self.db_connections,
            'all_file_items': self.all_file_items
        })
        dj_context = copy.copy(context)
        del dj_context['view']
        context.update({'context': json.dumps(dj_context)})
        return context

    def async_task(self, task_name):
        return self.fetch_from_db(task_name)

    def async_tasks(self, task_name=None):
        if task_name:
            return [task_name]
        async_tasks = dict(self.file_items, **self.test_file_items)
        return [task_name for task_name in async_tasks]
