import factory

from faker import Factory as FakerFactory
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from django.test import TestCase
from django.db import models
from collections import OrderedDict
from edc_rdb.pims_reference import func_str, BaseReference, DuplicateKeyError

faker = FakerFactory.create()


class Reference(BaseReference):

    sources = OrderedDict([
        ('default', OrderedDict([
            ('subject_identifier', getattr),
            ('first_name', getattr),
            ('last_name', getattr),
            ('dob', getattr),
            ('gender', getattr),
            ('omang', func_str),
        ])),
    ])


class TestModel(models.Model):

    subject_identifier = models.CharField(max_length=25)
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    dob = models.DateField(default=date.today())
    gender = models.CharField(max_length=25)
    omang = models.CharField(max_length=25)
    thing1 = models.CharField(max_length=25, null=True)
    thing2 = models.CharField(max_length=25, null=True)

    class Meta:
        app_label = 'edc_rdb'


class TestModelFactory(factory.DjangoModelFactory):

    class Meta:
        model = TestModel

    subject_identifier = factory.Sequence(lambda x: '{}'.format(x))
    first_name = factory.LazyAttribute(lambda x: 'E{}'.format(faker.first_name().upper())),
    last_name = factory.LazyAttribute(lambda x: 'E{}'.format(faker.last_name().upper())),
    gender = 'F',
    omang = factory.Sequence(lambda x: '12345678{}'.format(x))
    dob = date.today() - relativedelta(years=25)


class TestReference(TestCase):

    def test_none(self):
        subjects = {}
        reference = Reference(subjects)
        self.assertEqual(reference.data, {})

    def test_malformed_values_list(self):
        subjects = {'erik': [1]}
        with self.assertRaises(TypeError) as cm:
            Reference(subjects)
        self.assertIn('missing 5 required positional arguments', str(cm.exception))
        self.assertIn('\'first_name\', \'last_name\', \'dob\', \'gender\', and \'omang\'', str(cm.exception))

    def test_values_list(self):
        dob = datetime.today()
        values = [1, 'FIRST', 'LAST', dob, 'F', '123456789']
        subjects = {'erik': values}
        reference = Reference(subjects)
        for subject in reference.data.values():
            self.assertEqual(subject.subject_identifier, 1)
            self.assertEqual(subject.first_name, 'FIRST')
            self.assertEqual(subject.last_name, 'LAST')
            self.assertEqual(subject.dob, dob)
            self.assertEqual(subject.gender, 'F')
            self.assertEqual(subject.omang, '123456789')

    def test_fields_from_source(self):
        dob = datetime.today()
        values = [1, 'FIRST', 'LAST', dob, 'F', '123456789']
        subjects = {'erik': values}
        reference = Reference(subjects)
        for subject in reference.data.values():
            self.assertEqual(subject._fields,
                             ('subject_identifier', 'first_name', 'last_name', 'dob', 'gender', 'omang'))

    def test_data_keys(self):
        dob = datetime.today()
        values = [1, 'FIRST', 'LAST', dob, 'F', '123456789']
        subjects = {'erik': values}
        reference = Reference(subjects)
        self.assertEqual([k for k in reference.data.keys()], ['1'])

    def test_key_field(self):
        dob = datetime.today()
        values = [1, 'FIRST', 'LAST', dob, 'F', '123456789']
        subjects = {'1': values}
        reference = Reference(subjects)
        self.assertEqual(reference.key_field, 'subject_identifier')

    def test_bad_key_field(self):
        dob = datetime.today()
        values = [1, 'FIRST', 'LAST', dob, 'F', '123456789']
        subjects = {'erik': values}
        self.assertRaises(ValueError, Reference, subjects, key_field='subject_id')

    def test_duplicate_key(self):
        dob = datetime.today()
        subjects = {'1': [1, 'FIRST1', 'LAST', dob, 'F', '123456789'],
                    '2': [1, 'FIRST2', 'LAST', dob, 'F', '123456789']}
        self.assertRaises(DuplicateKeyError, Reference, subjects)

    def test_accepts_list_of_lists(self):
        dob = datetime.today()
        subjects = [[1, 'FIRST1', 'LAST', dob, 'F', '123456789'], [2, 'FIRST2', 'LAST', dob, 'F', '123456789']]
        reference = Reference(subjects)
        keys = [k for k in reference.data.keys()]
        keys.sort()
        self.assertEqual(keys, ['1', '2'])

    def test_accepts_queryset(self):
        for _ in range(0, 10):
            TestModelFactory()
        subjects = TestModel.objects.all()
        reference = Reference(subjects)
        keys = [k for k in reference.data.keys()]
        keys.sort()
        self.assertEqual(keys, [str(n) for n in range(0, 10)])
