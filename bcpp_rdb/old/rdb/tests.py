from django.contrib.auth.models import User
from django.test import TestCase
from tastypie.test import ResourceTestCase
from tastypie.utils import make_naive

from .rdb import Rdb


class TestRdb(ResourceTestCase):

    def setUp(self):
        super(TestRdb, self).setUp()

        self.username = 'erik'
        self.password = 'pass'
        self.user = User.objects.create_user(self.username, 'erik@example.com', self.password)

    def get_credentials(self):
        return self.create_basic(username=self.username, password=self.password)

    def test_api(self):
        rdb = Rdb()
        resp = self.api_client.post(rdb.edc_url, format='json', data={})
        self.assertHttpUnauthorized(resp)

    def test_(self):
        rdb = Rdb()
        # rdb.add_or_update_subjects_from_bhs_consent()
