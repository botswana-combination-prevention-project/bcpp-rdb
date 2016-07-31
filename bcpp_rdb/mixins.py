import asyncio
import json
import os
import pytz
import pandas as pd

from datetime import datetime
from django.conf import settings
from django.http.response import HttpResponse
from sqlalchemy.engine import create_engine

from .private_settings import Rdb, Edc

tz = pytz.timezone(settings.TIME_ZONE)


def get_statinfo(path, filename):
    statinfo = os.stat(os.path.join(path, filename))
    return {
        'path': path,
        'filename': filename,
        'name': filename.split('.')[0],
        'size': statinfo.st_size,
        'timestamp': tz.localize(datetime.fromtimestamp(statinfo.st_mtime)).isoformat()[0:10],
    }


class AsyncMixin:

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.is_ajax():
            futures = {}
            task_response_data = {}
            tasks = []
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop = asyncio.get_event_loop()
            for task_name in self.async_tasks(self.kwargs.get('task_name')):
                futures[task_name] = asyncio.Future()
                tasks.append(self._task(futures[task_name], task_name))
            loop.run_until_complete(asyncio.wait(tasks))
            for task_name, future in futures.items():
                task_response_data[task_name] = future.result()
            loop.close()
            print(task_response_data)
            return HttpResponse(json.dumps(task_response_data), content_type='application/json')
        return self.render_to_response(context)

    @asyncio.coroutine
    def _task(self, future, task_name):
        future.set_result(self.async_task(task_name))

    def async_task(self, name):
        """Override."""
        return {}

    def async_tasks(self, task_name=None):
        """Override."""
        return {}


class FileItemsMixin:

    _files = []
    file_exts = ['.csv']
    upload_folder = settings.UPLOAD_FOLDER
    file_items = {}
    test_file_items = {}
    static_file_items = {}

    def add_file_item(self, item_name, item_verbose_name):
        """Add a file_item to the dict of file_items.

        Call this from your concrete class, for example:

            self.add_file_item('pims_haart', 'PIMS Haart data')

        """
        self.file_items[item_name] = dict(
            name=item_name,
            verbose_name=item_verbose_name,
            current_file=self.current_file(item_name),
            archived_files=self.archived_files(item_name))

    def add_test_file_item(self, item_name, item_verbose_name):
        self.test_file_items[item_name] = dict(
            name=item_name,
            verbose_name=item_verbose_name,
            current_file=self.current_file(item_name),
            archived_files=self.archived_files(item_name))

    def add_static_file_item(self, item_name, item_verbose_name):
        """Return a dict. These file items are not updateable."""
        self.static_file_items[item_name] = dict(
            name=item_name,
            verbose_name=item_verbose_name,
            current_file=self.current_file(item_name),
            archived_files=self.archived_files(item_name))

    @property
    def file_item_names(self):
        return [key for key in self.file_items]

    @property
    def all_file_items(self):
        d = {}
        d['file_items'] = {name: {'verbose_name': file_item.get('verbose_name'), 'category': 'file'} for name, file_item in self.file_items.items()}
        d['test_file_items'] = {name: {'verbose_name': file_item.get('verbose_name'), 'category': 'test'} for name, file_item in self.test_file_items.items()}
        d['static_file_items'] = {name: {'verbose_name': file_item.get('verbose_name'), 'category': 'static'} for name, file_item in self.static_file_items.items()}
        return d

    def current_file(self, file_item_name):
        """Return a descriptive dictionary of the current file for the given item name."""
        files = [f for f in self.files if file_item_name in f.get('filename')]
        try:
            current_file = files[0]
        except IndexError:
            current_file = None
        return current_file

    def archived_files(self, file_item_name):
        """Return a dict of archived file descriptive dictionaries for the given item name."""
        archived_files = [f for f in self.files if file_item_name in f.get('filename')][1:]
        return {f.get('filename'): f for f in archived_files}

    @property
    def files(self):
        """Return a list of files from the upload folder."""
        if not self._files:
            stat_results = []
            for fname in [f for f in os.listdir(self.upload_folder) if any(f.endswith(ext) for ext in self.file_exts)]:
                stat_results.append(get_statinfo(self.upload_folder, fname))
            stat_results.sort(key=lambda i: i.get('timestamp'), reverse=True)
            self._files = stat_results
        return self._files


class DataframeMixin:

    conn_settings = Rdb, Edc

    def __init__(self, *args, **kwargs):
        super(DataframeMixin, self).__init__(*args, **kwargs)
        string = None
        self.engine = {}
        self.db_connections = {}
        for settings in self.conn_settings:
            if settings.engine == 'pg':
                string = 'postgresql://{user}:{password}@{host}:{port}/{dbname}'
            elif settings.engine == 'mysql':
                string = 'mysql+mysqldb://{user}:{password}@{host}:{port}/{dbname}'
            string = string.format(
                user=settings.user,
                password=settings.password,
                host=settings.host,
                dbname=settings.dbname,
                port=settings.port)
            self.engine[settings.connection_name] = self.open_engine(string)
            self.db_connections[settings.connection_name] = dict(
                name=settings.connection_name,
                host=settings.host,
                dbname=settings.dbname,
                port=settings.port)

    def open_engine(self, string):
        connect_args = {}
        try:
            if settings.timeout:
                connect_args = {'connect_timeout': settings.timeout}
            else:
                connect_args = {}
        except AttributeError:
            pass
        return create_engine(string, connect_args=connect_args)

    def get_dataframe(self, sql=None, connection_name=None):
        """Return a dataframe for the sql query."""
        with self.engine[connection_name].connect() as conn, conn.begin():
            dataframe = pd.read_sql_query(sql, conn)
        return dataframe
