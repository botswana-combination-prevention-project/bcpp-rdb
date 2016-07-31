import os
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.conf import settings
from bcpp_rdb.views import HomeView


class TestRdb(TestCase):

    def setUp(self):
        self.test_files = {}
        path = settings.UPLOAD_FOLDER
        self.test_files['test-pims-haart'] = []
        for i in range(0, 5):
            fname = 'test-pims-haart-{}'.format(timezone.now().strftime('%Y%m%d%H%m%f'))
            fname = os.path.join(path, fname)
            t = (timezone.now() - timedelta(i)).toordinal()
            self.touch(fname, times=(t, t))
            self.test_files['test-pims-haart'].append(fname)
        self.test_files['test-pims-hiv'] = []
        for i in range(0, 5):
            fname = 'test-pims-hiv-{}'.format(timezone.now().strftime('%Y%m%d%H%m%f'))
            fname = os.path.join(path, fname)
            t = (timezone.now() - timedelta(i)).toordinal()
            self.touch(fname, times=(t, t))
            self.test_files['test-pims-hiv'].append(fname)

    def tearDown(self):
        for test_files in self.test_files.values():
            for fname in test_files:
                os.remove(fname)

    def touch(self, fname, times=None):
        with open(fname, 'a'):
            os.utime(fname, times=times)

    def test_files(self):
        """Assert method finds correct files for the given label."""
        h = HomeView()
        self.assertIsInstance(h.current_file('pims-haart'), tuple)
        self.assertEqual(len(h.archived_files('pims-haart')), 4)

    def test_file_attr(self):
        """Assert method finds correct files for the given label."""
        h = HomeView()
        f = h.current_file('pims-haart')
        self.assertTrue('pims-haart' in f.filename)
        self.assertTrue(f.timestamp)
        self.assertTrue(f.path == settings.UPLOAD_FOLDER)
        self.assertTrue(f.size == 0)

    def test_rdb_file_attr(self):
        """Assert method finds correct files for the given label."""
        h = HomeView()
        for rdb_file in h.rdb_files:
            self.assertTrue('pims-haart' in rdb_file.current_file.filename)
            self.assertTrue(rdb_file.current_file.timestamp)
            self.assertTrue(rdb_file.current_file.path == settings.UPLOAD_FOLDER)
            self.assertTrue(rdb_file.current_file.size == 0)
