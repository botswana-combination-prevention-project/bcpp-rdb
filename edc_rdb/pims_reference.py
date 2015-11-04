"""
find gender, age, dob, arv_naive
"""
import csv
import hashlib
import os
import pytz

from collections import namedtuple, OrderedDict
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.conf import settings

from bcpp.models import SubjectConsent  # note: does not decrypt omang
from rdb.rdb_models import Dimcurrentpimspatient, Factpimshaartinitiation, Dimpimshaartinitiation
from django.utils.timezone import make_aware
from django.db.models.query import QuerySet

tz = pytz.timezone(settings.TIME_ZONE)


def func_age(obj, attr):
    return relativedelta(obj.consent_datetime.date(), obj.dob).years


def func_str(obj, attr):
    return str(getattr(obj, attr))


def func_parse(obj, attr):
    value = str(getattr(obj, attr))
    return make_aware(parse(value), tz)


class DuplicateKeyError(Exception):
    pass


class BaseReference:

    sources = {'default': OrderedDict((('subject_identifier', getattr), ))}
    additional_fields = []
    exclude_fields_on_export = []

    def __init__(self, subjects, key_field=None, verbose=None):
        self.data = {}
        self.errmsg = None
        self.verbose = verbose
        self.key_field = key_field or next(iter(self.sources['default']))
        self.validate_sources()
        try:
            self.count = subjects.count()
        except (TypeError, AttributeError):
            self.count = len(subjects)
        self.subjects = self.get_subjects(subjects)
        self.subject_tuple = self.get_subject_tuple()
        self.query()

    def validate_sources(self):
        for value in self.sources.values():
            if not isinstance(value, OrderedDict):
                raise TypeError('Class attribute \'sources\' must be a dictionary of OrderedDicts')
        if self.key_field not in self.sources.get('default'):
            raise ValueError(
                'Field name not listed in \'default\' source fields. Expected on of {}. Got {}'.format(
                    self.sources.get('default').keys(), self.key_field))

    def query(self):
        n = 0
        for subject in self.subjects:
            data_values = self.get_data(subject)
            try:
                key_value = str(getattr(subject, self.key_field))
                self.data[key_value]
                raise DuplicateKeyError('Duplicate {}. Got {}.'.format(
                    self.key_field, key_value))
            except KeyError:
                self.data[str(getattr(subject, self.key_field))] = self.subject_tuple(*data_values)
            if self.verbose:
                n += 1
                print('{}/{} {} {}'.format(
                    n, self.count, key_value, self.data[key_value].errmsg))

    def requery(self):
        self.data = {}
        self.query()

    def get_subjects(self, subjects):
        """Returns a generator of named tuples.

        param subjects can be a Queryset, list of lists or a dictionary.

        The fields and their order in the default source correspond to the list of values
        from the "subjects" dictionary."""
        field_names = self.sources.get('default').keys()
        namedtpl = namedtuple('values', ' '.join(field_names))
        if isinstance(subjects, QuerySet):
            for subject in subjects:
                yield namedtpl(*[getattr(subject, attr) for attr in field_names])
        elif isinstance(subjects, dict):
            for subject in subjects.values():
                yield namedtpl(*subject)
        else:
            for subject in subjects:
                yield namedtpl(*subject)

    def get_subject_tuple(self):
        """Returns a named tuple class to store/represent each subject's data."""
        field_names = []
        for source_field in self.sources.values():
            field_names.extend([field_name for field_name in source_field])
        field_names.extend(self.additional_fields)
        return namedtuple('Subject', ('{}').format(' '.join(field_names)))

    def get_data(self, subject):
        """Returns the data_values as a list for the subject to be passed to the namedtuple (subject_tuple).

        If additional keys are added to the self.sources dictionary, code needs to be
        added here to handle them.
        """
        return self.get_data_from_source(subject)

    def get_data_from_source(self, obj, source_name=None):
        """Returns a list of source field values given the source instance and the source name.

        The source name is used to get the fields dictionary from self.sources."""
        fields = self.sources.get(source_name or 'default')
        if not fields:
            raise KeyError('Not found in sources field list. Got {}.'.format(source_name))
        if not obj:
            values = [None] * len(fields)
        else:
            values = []
            for attr, func in fields.items():
                values.append(func(obj, attr))
        return values

    def update_errmsg(self, source_name):
        """Sets, if none, and returns the errmsg."""
        if not self.errmsg:
            self.errmsg = 'not found in {}'.format(source_name)
        return self.errmsg

    def export_as_csv(self, path, exclude_fields_on_export=None):
        exclude_fields_on_export = exclude_fields_on_export or self.exclude_fields_on_export
        with open(os.path.expanduser(path), 'w') as f:
            writer = csv.writer(f)
            header = list(self.subject_tuple._fields)
            for fld in self.exclude_fields_on_export:
                header.pop(header.index(fld))
            writer.writerow(header)
            for key, subject in self.data.items():
                if self.verbose:
                    print('writing {}. {}'.format(key, subject.errmsg))
                writer.writerow([getattr(subject, fld) for fld in header])


class PimsReference(BaseReference):

    """A class to lookup BCPP survey subjects in the CDC "research database".

    Most subjects will appear in the bhs/ahs table (as model StudyParticipant). If not
    the hashed omang is used to directly query the PIMS tables.

    Usage:

        from edc_rdb.pims_reference import Subject, PimsReference

        # a dictionary of subject identifier and values
        subjects = {<subject_identifier>: [<subject_identifier>, <first_name>, <last_name>, <dob>, <gender>, <omang>], ...}
        pims_reference = PimsReference(subjects)
        pims_reference.export_to_csv(<your filename with path>)

    """

    sources = {
        'default': OrderedDict([
            ('subject_identifier', getattr),
            ('first_name', getattr),
            ('last_name', getattr),
            ('dob', getattr),
            ('gender', getattr),
            ('omang', func_str)]),
        'SubjectConsent': OrderedDict([
            ('consent_datetime', getattr),
            ('identity', getattr),
            ('age', func_age)]),
        'Dimcurrentpimspatient': OrderedDict([
            ('pimsclinicname', getattr),
            ('regdate', getattr)]),
        'Factpimshaartinitiation': OrderedDict([
            ('initiationdatekey', func_parse)]),
        'Dimpimshaartinitiation': OrderedDict([
            ('regimenline', getattr)]),
    }

    additional_fields = ['omang_hash', 'errmsg']
    exclude_fields_on_export = []

    def get_data(self, subject):
        """Returns the data_values list for the subject to be passed to the namedtuple (subject_tuple).

        If additional keys are added to the self.sources dictionary, code needs to be
        added here to handle them.
        """
        self.errmsg = None
        data_values = super(PimsReference, self).get_data(subject)
        subject_consent = self.get_subject_consent(subject_identifier=subject.subject_identifier)
        data_values.extend(self.get_data_from_source(subject_consent, 'SubjectConsent'))
        omang_hash = str(hashlib.sha256(subject.omang.encode()).hexdigest())
        dimcurrentpimspatient = self.get_dimcurrentpimspatient(omang_hash=omang_hash)
        data_values.extend(self.get_data_from_source(dimcurrentpimspatient, 'Dimcurrentpimspatient'))
        factpimshaartinitiation = self.get_factpimshaartinitiation(dimcurrentpimspatient=dimcurrentpimspatient)
        data_values.extend(self.get_data_from_source(factpimshaartinitiation, 'Factpimshaartinitiation'))
        dimpimshaartinitiation = self.get_dimpimshaartinitiation(factpimshaartinitiation=factpimshaartinitiation)
        data_values.extend(self.get_data_from_source(dimpimshaartinitiation, 'Dimpimshaartinitiation'))
        data_values.append(omang_hash)
        data_values.append(self.errmsg or 'OK')
        return data_values

    def get_subject_consent(self, **kwargs):
        try:
            obj = SubjectConsent.objects.filter(
                subject_identifier=kwargs.get('subject_identifier')).earliest('consent_datetime')
        except ObjectDoesNotExist:
            obj = None
            self.update_errmsg('SubjectConsent')
        return obj

    def get_dimcurrentpimspatient(self, **kwargs):
        try:
            obj = Dimcurrentpimspatient.objects.get(idno=kwargs.get('omang_hash'))
        except ObjectDoesNotExist:
            obj = None
            self.update_errmsg('Dimcurrentpimspatient')
        return obj

    def get_factpimshaartinitiation(self, **kwargs):
        try:
            obj = Factpimshaartinitiation.objects.get(
                dimcurrentpimspatientkey=kwargs.get('dimcurrentpimspatient').id)
        except MultipleObjectsReturned:
            obj = Factpimshaartinitiation.objects.filter(
                dimcurrentpimspatientkey=kwargs.get('dimcurrentpimspatient').id)[0]
        except (AttributeError, ObjectDoesNotExist):
            obj = None
            self.update_errmsg('Factpimshaartinitiation')
        return obj

    def get_dimpimshaartinitiation(self, **kwargs):
        try:
            obj = Dimpimshaartinitiation.objects.get(
                id=kwargs.get('factpimshaartinitiation').dimpimshaartinitiationkey)
        except (AttributeError, ObjectDoesNotExist):
            obj = None
            self.update_errmsg('Dimpimshaartinitiation')
        return obj
