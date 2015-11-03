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

tz = pytz.timezone(settings.TIME_ZONE)


def func_age(obj, attr):
    return relativedelta(obj.consent_datetime.date(), obj.dob).years


def func_str(obj, attr):
    return str(getattr(obj, attr))


def func_parse(obj, attr):
    value = str(getattr(obj, attr))
    return make_aware(parse(value), tz)


class BaseReference:

    sources = OrderedDict([('default', OrderedDict([('subject_identifier', getattr)]))])  # for example
    additional_fields = []
    exclude_fields_on_export = []

    def __init__(self, subjects, verbose=None):
        self.data = {}
        self.verbose = verbose
        self.subjects = self.get_subjects(subjects)
        self.subject_tuple = self.get_subject_tuple()
        self.query()

    def query(self):
        n = 0
        tot = len(self.subjects)
        for _, subject in self.subjects.items():
            values = self.get_values(subject)
            self.data[subject.subject_identifier] = self.subject_tuple(*values)
            if self.verbose:
                n += 1
                print('{}/{} {} {}'.format(
                    n, tot, subject.subject_identifier, self.data[subject.subject_identifier].errmsg))

    def requery(self):
        self.data = {}
        self.query()

    def get_subjects(self, subjects):
        """Returns a dictionary of named tuples by subject_identifier using the "default" source.

        The fields and their order in the default source correspond to the list of values
        from the "subjects" dictionary."""
        dct = {}
        field_names = self.sources.get('default').keys()
        namedtpl = namedtuple('values', ' '.join(field_names))
        for subject_id, values in subjects.items():
            dct.update({subject_id: namedtpl(*values)})
        return dct

    def get_subject_tuple(self):
        """Returns a named tuple class to store/represent each subject's data."""
        field_names = []
        for source_field in self.sources.values():
            field_names.extend([field_name for field_name in source_field])
        field_names.extend(self.additional_fields)
        return namedtuple('Subject', ('{}').format(' '.join(field_names)))

    def get_values(self, subject):
        """Returns the values list for the subject to be passed to the namedtuple (subject_tuple).

        If additional keys are added to the self.sources dictionary, code needs to be
        added here to handle them.
        """
        return self.get_source_values(subject)

    def get_source_values(self, obj, source_name=None):
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

    def export_as_csv(self, path, exclude_fields_on_export=None):
        exclude_fields_on_export = exclude_fields_on_export or self.exclude_fields_on_export
        with open(os.path.expanduser(path), 'w') as f:
            writer = csv.writer(f)
            header = list(self.subject_tuple._fields)
            for fld in self.exclude_fields_on_export:
                header.pop(header.index(fld))
            writer.writerow(header)
            for subject_identifier, subject in self.data.items():
                if self.verbose:
                    print('writing {}. {}'.format(subject_identifier, subject.errmsg))
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

    sources = OrderedDict([
        ('default', OrderedDict([
            ('subject_identifier', getattr),
            ('first_name', getattr),
            ('last_name', getattr),
            ('dob', getattr),
            ('gender', getattr),
            ('omang', func_str),
        ])),
        ('SubjectConsent', OrderedDict([
            ('consent_datetime', getattr),
            ('identity', getattr),
            ('age', func_age),
        ])),
        ('Dimcurrentpimspatient', OrderedDict([
            ('pimsclinicname', getattr),
            ('regdate', getattr),
        ])),
        ('Factpimshaartinitiation', OrderedDict([
            ('initiationdatekey', func_parse)])),
        ('Dimpimshaartinitiation', OrderedDict([
            ('regimenline', getattr),
        ]))
    ])

    additional_fields = ['omang_hash', 'errmsg']
    exclude_fields_on_export = []

    def get_values(self, subject):
        """Returns the values list for the subject to be passed to the namedtuple (subject_tuple).

        If additional keys are added to the self.sources dictionary, code needs to be
        added here to handle them.
        """
        errmsg = None
        values = super(PimsReference, self).get_values(subject)
        subject_consent = self.get_subject_consent(subject_identifier=subject.subject_identifier)
        values.extend(self.get_source_values(subject_consent, 'SubjectConsent'))
        omang_hash = self.omang_hasher(subject.omang)
        pims_patient = self.get_dimcurrentpimspatient(omang_hash=omang_hash)
        if not pims_patient:
            errmsg = self.get_errmsg('Dimcurrentpimspatient', errmsg)
        values.extend(self.get_source_values(pims_patient, 'Dimcurrentpimspatient'))
        haart_initiation = self.get_factpimshaartinitiation(pims_patient=pims_patient)
        if not haart_initiation:
            errmsg = self.get_errmsg('Factpimshaartinitiation', errmsg)
        values.extend(self.get_source_values(haart_initiation, 'Factpimshaartinitiation'))
        haart = self.get_dimpimshaartinitiation(haart_initiation=haart_initiation)
        if not haart:
            errmsg = self.get_errmsg('Dimpimshaartinitiation', errmsg)
        values.extend(self.get_source_values(haart, 'Dimpimshaartinitiation'))
        values.append(omang_hash)
        values.append(errmsg or 'OK')
        return values

    def get_subject_consent(self, **kwargs):
        try:
            obj = SubjectConsent.objects.filter(
                subject_identifier=kwargs.get('subject_identifier')).earliest('consent_datetime')
        except ObjectDoesNotExist:
            obj = None
        return obj

    def get_dimcurrentpimspatient(self, **kwargs):
        try:
            obj = Dimcurrentpimspatient.objects.get(idno=kwargs.get('omang_hash'))
        except ObjectDoesNotExist:
            obj = None
        return obj

    def get_factpimshaartinitiation(self, **kwargs):
        try:
            obj = Factpimshaartinitiation.objects.get(
                dimcurrentpimspatientkey=kwargs.get('pims_patient').id)
        except MultipleObjectsReturned:
            obj = Factpimshaartinitiation.objects.filter(
                dimcurrentpimspatientkey=kwargs.get('pims_patient').id)[0]
        except (AttributeError, ObjectDoesNotExist):
            obj = None
        return obj

    def get_dimpimshaartinitiation(self, **kwargs):
        try:
            obj = Dimpimshaartinitiation.objects.get(
                id=kwargs.get('haart_initiation').dimpimshaartinitiationkey)
        except (AttributeError, ObjectDoesNotExist):
            obj = None
        return obj

    def get_errmsg(self, source_name, errmsg=None):
        if errmsg:
            return errmsg
        return 'not found in {}'.format(source_name)

    def omang_hasher(self, omang):
        return str(hashlib.sha256(omang.encode()).hexdigest())
