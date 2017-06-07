import copy
import json
import pytz

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from edc_base.view_mixins import EdcBaseViewMixin

from ..mixins import FileItemsMixin, AsyncMixin
from .query_mixin import QueryMixin

tz = pytz.timezone(settings.TIME_ZONE)


class HomeView(EdcBaseViewMixin, FileItemsMixin, AsyncMixin, QueryMixin, TemplateView):

    template_name = 'bcpp_rdb/home.html'
    response_data = {}

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        self.add_file_item('pims_haart', 'PIMS Haart data')
        self.add_file_item('pims', 'PIMS data')
        self.add_file_item('htc', 'HTC data')
        self.add_file_item('bcpp_subjects', 'BCPP Subjects')
        self.add_file_item('bcpp_requisitions', 'BCPP Requisitions')
        self.add_test_file_item('bcpp_test', 'BCPP Test')
        self.add_test_file_item('rdb_test', 'RDB Test')
        self.add_static_file_item('bcpp_rdb_key', 'BCPP/RDB Subject Key')
        context = super(HomeView, self).get_context_data(**kwargs)
        context.update({
            'all_file_items': self.all_file_items,
            'connections': self.db_connections,
            'file_items': self.file_items,
            'static_file_items': self.static_file_items,
            'test_file_items': self.test_file_items,
            'upload_url': settings.UPLOAD_URL,
        })

        dj_context = copy.copy(context)
        dj_context.pop('view')
        dj_context.pop('navbar')
        dj_context.pop('navbar_item_selected')
        context.update({'context': json.dumps(dj_context)})
        return context

    def async_task(self, task_name):
        return self.fetch_from_db(task_name)

    def async_tasks(self, task_name=None):
        if task_name:
            return [task_name]
        async_tasks = dict(self.file_items, **self.test_file_items)
        return [task_name for task_name in async_tasks]
