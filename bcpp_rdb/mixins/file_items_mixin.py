import os
import pytz

from datetime import datetime
from django.conf import settings

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
        d['file_items'] = {name: {'verbose_name': file_item.get(
            'verbose_name'), 'category': 'file'} for name, file_item in self.file_items.items()}
        d['test_file_items'] = {name: {'verbose_name': file_item.get(
            'verbose_name'), 'category': 'test'} for name, file_item in self.test_file_items.items()}
        d['static_file_items'] = {name: {'verbose_name': file_item.get(
            'verbose_name'), 'category': 'static'} for name, file_item in self.static_file_items.items()}
        return d

    def current_file(self, file_item_name):
        """Return a descriptive dictionary of the current file
        for the given item name.
        """
        files = [f for f in self.files if file_item_name in f.get('filename')]
        try:
            current_file = files[0]
        except IndexError:
            current_file = None
        return current_file

    def archived_files(self, file_item_name):
        """Return a dict of archived file descriptive dictionaries
        for the given item name.
        """
        archived_files = [
            f for f in self.files if file_item_name in f.get('filename')][1:]
        return {f.get('filename'): f for f in archived_files}

    @property
    def files(self):
        """Return a list of files from the upload folder.
        """
        if not self._files:
            stat_results = []
            for fname in [f for f in os.listdir(self.upload_folder) if any(f.endswith(ext) for ext in self.file_exts)]:
                stat_results.append(get_statinfo(self.upload_folder, fname))
            stat_results.sort(key=lambda i: i.get('timestamp'), reverse=True)
            self._files = stat_results
        return self._files
