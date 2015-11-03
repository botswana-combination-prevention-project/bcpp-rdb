"""
find gender, age, dob, arv_naive
"""
import csv
import hashlib
import os
import pytz

from collections import namedtuple, OrderedDict
from dateutil.relativedelta import relativedelta
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.conf import settings

from bcpp.models import SubjectConsent  # note: does not decrypt omang
from rdb.rdb_models import Dimcurrentpimspatient, Factpimshaartinitiation, Dimpimshaartinitiation

tz = pytz.timezone(settings.TIME_ZONE)

Subject = namedtuple(
    'Subject',
    ('subject_identifier consent_datetime omang gender age omang_hash '
     'pims_clinic pims_registration pims_regimen pims_initiation_date '
     'errmsg')
)


def func_age(subject_consent, attr):
    return relativedelta(subject_consent.consent_datetime.date(), subject_consent.dob).years


class PimsReference:

    """A class to lookup BCPP survey subjects in the CDC "research database".

    Most subjects will appear in the bhs/ahs table (as model StudyParticipant). If not
    the hashed omang is used to directly query the PIMS tables.

    Usage:

        from edc_rdb.pims_reference import Subject, PimsReference

        subjects = {<subject_identifier>: [<subject_identifier>, <omang>], ...}
        pims_reference = PimsReference(subjects)
        pims_reference.export_to_csv(<your filename with path>)

    """

    models = OrderedDict([
        ('SubjectConsent', OrderedDict([
            ('consent_datetime', getattr),
            ('identity', getattr),
            ('gender', getattr),
            ('age', func_age),
        ])),
        ('Dimcurrentpimspatient', OrderedDict([
            ('pimsclinicname', getattr),
            ('regdate', getattr),
            # ('pims_regimen', getattr),
            # ('pims_initiation_date', getattr),
        ])),
        ('Factpimshaartinitiation', OrderedDict([
            # ('pimsclinicname', getattr),
            ('initiationdatekey', getattr)])),
        ('Dimpimshaartinitiation', OrderedDict([
            ('regimenline', getattr),
        ]))
    ])

    exclude_fields_on_export = ['identity']

    def __init__(self, subjects=None, models=None):
        fields = []
        self.subject_data = {}
        self.subjects = subjects
        self.models = models or self.models
        for fields_dict in self.models.values():
            fields.extend([field for field in fields_dict])
        self.subject_tuple = namedtuple(
            'Subject', ('subject_identifier omang_hash {} errmsg').format(' '.join(fields)))
        for _, subject in self.subjects.items():
            subject_identifier, omang = subject
            omang_hash = self.omang_hasher(omang)
            values = self.get_values(subject_identifier, omang_hash)
            self.subject_data[subject_identifier] = self.subject_tuple(*values)

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

    def get_values(self, subject_identifier, omang_hash):
        """Returns the values list for the subject to be passed to the namedtuple (subject_tuple).

        If additional keys are added to the self.models dictionary, code needs to be
        added here to handle them.
        """
        errmsg = None
        values = [subject_identifier, omang_hash]
        subject_consent = self.get_subject_consent(subject_identifier=subject_identifier)
        values.extend(self.get_object_values(subject_consent, 'SubjectConsent'))
        pims_patient = self.get_dimcurrentpimspatient(omang_hash=omang_hash)
        if not pims_patient:
            errmsg = self.get_errmsg('Dimcurrentpimspatient', errmsg)
        values.extend(self.get_object_values(pims_patient, 'Dimcurrentpimspatient'))
        haart_initiation = self.get_factpimshaartinitiation(pims_patient=pims_patient)
        if not haart_initiation:
            errmsg = self.get_errmsg('Factpimshaartinitiation', errmsg)
        values.extend(self.get_object_values(haart_initiation, 'Factpimshaartinitiation'))
        haart = self.get_dimpimshaartinitiation(haart_initiation=haart_initiation)
        if not haart:
            errmsg = self.get_errmsg('Dimpimshaartinitiation', errmsg)
        values.extend(self.get_object_values(haart, 'Dimpimshaartinitiation'))
        values.append(errmsg or 'OK')
        return values

    def get_object_values(self, obj, model_name):
        """Returns a list of model field values given the model instance and the model name.

        The model name is used to get the fields dictionary from self.models."""
        fields = self.models.get(model_name)
        if not fields:
            raise KeyError('Not found in models dictionary. Got {}.'.format(model_name))
        if not obj:
            values = [None] * len(fields)
        else:
            values = []
            for attr, func in fields.items():
                values.append(func(obj, attr))
        return values

    def get_errmsg(self, model_name, errmsg=None):
        if errmsg:
            return errmsg
        return 'not found in {}'.format(model_name)

    def export_as_csv(self, path):
        with open(os.path.expanduser(path), 'w') as f:
            writer = csv.writer(f)
            export_fields = self.subject_tuple._fields
            for fld in self.exclude_fields_on_export:
                export_fields.pop(export_fields.index(fld))
            writer.writerow(export_fields)
            for subject_identifier, subject in self.subject_data.items():
                print('writing {}. {}'.format(subject_identifier, subject.errmsg))
                writer.writerow([getattr(subject, fld) for fld in export_fields])

    def omang_hasher(self, omang):
        return str(hashlib.sha256(omang.encode()).hexdigest())
