from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import hashlib
import pytz
import re
import requests
import sys

from dateutil import parser

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError
from django.db.models import Q
from edc_rdb.models import Subject, Result, BhsSubject, HtcSubject, ClinicSubject, SmcSubject, BhsLabHistory

from .models import StudyParticipant, BhsParticipant, SmcParticipant, EnrollmentCcc, PimsLab
from .patterns import BHS_PATTERN, CLINIC_PATTERN, HTC_PATTERN, CCC_PATTERN
from edc_rdb.communities import bhs, htc, clinic

from dateutil.relativedelta import relativedelta

tz = pytz.timezone(settings.TIME_ZONE)


class Rdb(object):

    """Create a set of tables that combine Edc, Rdb data for BHS and HTC subjects.

    For example:

        from rdb.edb import Rdb
        from edc_rdb import BhsSubject, BhsLabHistory

        rdb = Rdb()
        # populate BhsSubject
        rdb.add_or_update_subjects_from_bhs_consent()
        # update referral values in BhsSubject
        rdb.update_bhs_subjects_from_referral()
        # add to BhsLabHistory CD4 and VL values from PIMS in the RDB
        rdb.add_or_update_pims_labs(BhsLabHistory)

    BHS
    ---
    93% vl < 40
    96% vl < 400

    not diagnosed and eligible for treatment (new_pos, low cd4)

    After BHS
    ---------
    how long to be linked to care?
    retention (1yr out, 2yrs out)
    virologic suppression (excludes defaulters, mis-reports, stoppage) 90%
    non-citizens
    what of absentees?
    grade 3/4 creatinine at baseline (all and 50yrs+)

    from Lisa:
    - CD4>350 referrals – frequency of safety lab serious abnormalities?
      (informative re: necessity of safety labs prior to ART initiation, especially renal toxicity)
    - CD4<350 referrals – what was median CD4 at referral?  (compare to
      national data, shows what adding a major HTC push achieves in terms of
      identifying people previously not in care)
    - VL retention and suppression data among those referred, and among those in
      the clinic from the community overall – crucial
    - Per CPC - # of HIV-infected community residents not on ART but registered
      at that clinic (tells us # of ‘low-hanging fruit’)
    """

    def __init__(self, edc_url=None, filter_options=None):
        self.host = 'http://localhost:8000'
        self.edc_url = edc_url or 'http://localhost:8000/api/bcpp/'
        self.filter_options = filter_options or {}

    def study_participants(self):
        if self.filter_options:
            return StudyParticipant.objects.filter(**self.filter_options)
        else:
            StudyParticipant.objects.all()

    def add_subjects_from_rdb(self):
        """Fetch subjects from the RDB."""

        # check Oc

        for study_participant in self.study_participants():
            try:
                subject = Subject.objects.get(
                    omang_hash=study_participant.omang_hash[0:100],
                )
            except Subject.DoesNotExist:
                print(study_participant.omang_hash)
                subject = Subject()
                subject.omang_hash = study_participant.omang_hash[0:100]
            result = self.identifier(study_participant.htc_identifier, {})
            result = self.identifier(study_participant.bhs_identifier, result)
            subject.htc_identifier = result.get('htc_identifier', '')[0:50]
            subject.bhs_identifier = result.get('bhs_identifier', '')[0:50]
            subject.clinic_identifier = result.get('clinic_identifier', '')[0:50]
            subject.community = self.community(
                [subject.bhs_identifier, subject.htc_identifier, subject.clinic_identifier])
            subject.save(update_fields=[
                'omang_hash', 'htc_identifier', 'bhs_identifier', 'clinic_identifier', 'community'])
        Subject.objects.filter(htc_identifier='').update(htc_identifier=None)
        Subject.objects.filter(bhs_identifier='').update(bhs_identifier=None)
        Subject.objects.filter(clinic_identifier='').update(clinic_identifier=None)
        Subject.objects.filter(bhs_identifier__isnull=False).update(bhs=True)
        Subject.objects.filter(htc_identifier__isnull=False).update(htc=True)

    def add_or_update_subjects_from_bhs_consent(self):
        """Adds BHS subjects from EDC subject_consent model."""
        n = 0
        added = 0
        next_url = '{}subject_consent/?format=json'.format(self.edc_url)
        while next_url:
            request = requests.get(next_url)
            next_url = None
            objects = request.json()['objects']
            total = request.json()['meta']['total_count']
            for obj in objects:
                n += 1
                try:
                    Subject.objects.get(bhs_identifier=obj.get('subject_identifier'))
                except Subject.DoesNotExist:
                    Subject.objects.create(
                        bhs_identifier=obj.get('subject_identifier'),
                        bhs=True,
                        omang=obj.get('identity'),
                        omang_hash=hashlib.sha256(obj.get('identity').encode()).hexdigest(),
                        dob=obj.get('dob'),
                        gender=obj.get('gender'),
                    )
                if request.json()['meta']['next']:
                    next_url = '{}{}'.format(self.host, request.json()['meta']['next'])
                sys.stdout.write('{0} of {1}. {2} added    \r'.format(n, total, added))
                sys.stdout.flush()

    def update_bhs_subjects_from_referral(self):
        """Adds or update BHS subjects from EDC subject_referral model."""
        n = 0
        added = 0
        next_url = '{}subject_referral/?format=json'.format(self.edc_url)
        while next_url:
            request = requests.get(next_url)
            next_url = None
            objects = request.json()['objects']
            total = request.json()['meta']['total_count']
            for obj in objects:
                n += 1
                try:
                    print(obj.get('subject_identifier'))
                    subject = BhsSubject.objects.get(identifier=obj.get('subject_identifier'))
                    referral_code = []
                    if subject.referral_code:
                        referral_code.append(subject.referral_code)
                    referral_code.append(obj.get('referral_code'))
                    subject.referral_code = ','.join(referral_code)
                    try:
                        subject.referral_appt_date = parser.parse(obj.get('referral_appt_date'))
                    except AttributeError:
                        pass
                    subject.referred = True if obj.get('subject_referred') == 'Yes' else False
                    subject.referral_hiv_result = obj.get('hiv_result')
                    subject.referral_new_pos = obj.get('new_pos')
                    subject.referral_on_art = obj.get('on_art')
                    subject.referral_vl_drawn = obj.get('vl_sample_drawn')
                    subject.referral_vl_datetime = parser.parse(obj.get('vl_sample_drawn_datetime'))
                    subject.save(update_fields=[
                        'referral_code', 'referral_appt_date', 'referred', 'referral_hiv_result',
                        'referral_on_art', 'referral_vl_datetime', 'referral_vl_drawn',
                        'referral_new_pos'])
                except BhsSubject.DoesNotExist:
                    print(obj.get('subject_identifier'))
                except MultipleObjectsReturned:
                    pass
                if request.json()['meta']['next']:
                    next_url = '{}{}'.format(self.host, request.json()['meta']['next'])
                sys.stdout.write('{0} of {1}. {2} added from edc   \r'.format(n, total, added))
                sys.stdout.flush()

    def update_subject_from_smc(self):
        """Update subjects in Subject from smc data in RDB."""
        n = 0
        for subject in Subject.objects.all():
            n += 1
            smc_identifier = self.smc_identifier(subject)
            if (subject.smc_identifier is not None and
                    subject.smc_identifier != smc_identifier):
                subject.smc = True
                subject.save(update_fields=['smc_identifier', 'smc'])
            sys.stdout.write('{0}  {1:100s}\r'.format(n, smc_identifier or ''))
            sys.stdout.flush()

    def add_or_update_pims_labs(self, subject_model_cls):
        """Retrieves VL results from PIMS tables for a subject listed in the subject model."""
        n = 0
        updated = 0
        total = subject_model_cls.objects.all().count()
        for subject in subject_model_cls.objects.all().order_by('omang'):
            n += 1
            for pims_lab in PimsLab.objects.filter(
                    pims_patient__omang_hash=subject.omang_hash,
                    pims_order__test_name__in=['Viral load', 'CD4%', 'CD4 count']):
                updated += 1 if self.add_or_update_lab_history(subject, pims_lab, BhsLabHistory) else 0
            sys.stdout.write('{0} of {1}. {2} updated for pims   \r'.format(n, total, updated))
            sys.stdout.flush()
        sys.stdout.write('\n')
        sys.stdout.flush()

    def add_or_update_lab_history(self, subject, pims_lab, lab_history_model):
        try:
            return lab_history_model.objects.create(
                subject=subject,
                laboratory=(
                    None if pims_lab.pims_order.testing_facility == 'unk'
                    else pims_lab.pims_order.testing_facility),
                sample_identifier=(
                    None if pims_lab.pims_order.external_specimen_no == 'unk'
                    else pims_lab.pims_order.external_specimen_no),
                order_identifier=pims_lab.pims_order.order_identifier,
                test_name=pims_lab.pims_order.test_name,
                sample_date=parser.parse(str(pims_lab.sample_datekey)),
                result_qualifier=None if pims_lab.result_qualifier == 'unk' else pims_lab.result_qualifier,
                result=pims_lab.result,
                result_dec=self.result_as_decimal(pims_lab.result),
                result_datetime=tz.localize(parser.parse(str(pims_lab.result_datekey))),
                status=pims_lab.pims_order.status,
                source='pims',
            )
        except IntegrityError:
            return None

    def identifier(self, identifier, result=None):
        result = result or {}
        if re.match(HTC_PATTERN, identifier):
            result.update({'htc_identifier': identifier})
        elif re.match(BHS_PATTERN, identifier):
            result.update({'bhs_identifier': identifier})
        elif re.match(CLINIC_PATTERN, identifier):
            result.update({'clinic_identifier': identifier})
        elif re.match(CCC_PATTERN, identifier):
            result.update({'ccc_identifier': identifier})
        return result

    def smc_identifier(self, study_participant):
        try:
            smc_participant = SmcParticipant.objects.get(
                Q(participant_id=study_participant.htc_identifier) |
                Q(participant_id=study_participant.bhs_identifier) |
                Q(omang_hash=study_participant.omang_hash)
            )
            participant_id = smc_participant.participant_id
            if participant_id == 'unk':
                participant_id = None
            omang_hash = smc_participant.omang_hash
            if smc_participant.omang_hash == 'unk':
                omang_hash = None
            return participant_id or omang_hash[0:100] or smc_participant.mergeid[0:100]
        except (SmcParticipant.DoesNotExist, MultipleObjectsReturned):
            return None

    def add_or_update_bhs_subjects(self):
        """Adds BHS subjects from EDC subject_consent model."""
        n = 0
        added = 0
        next_url = '{}subject_consent/?format=json'.format(self.edc_url)
        while next_url:
            request = requests.get(next_url)
            next_url = None
            objects = request.json()['objects']
            total = request.json()['meta']['total_count']
            for obj in objects:
                n += 1
                try:
                    bhs_subject = BhsSubject.objects.get(identifier=obj.get('subject_identifier'))
                except BhsSubject.DoesNotExist:
                    bhs_subject = BhsSubject(identifier=obj.get('subject_identifier'))
                bhs_subject.omang = obj.get('identity')
                bhs_subject.omang_hash = hashlib.sha256(obj.get('identity').encode()).hexdigest()
                bhs_subject.dob = obj.get('dob')
                bhs_subject.gender = self.gender(obj.get('gender'))
                bhs_subject.citizen = self.citizen(obj.get('citizen'))
                bhs_subject.age = self.age(obj.get('dob'))
                bhs_subject.services = 'bhs'
                bhs_subject.community_name = self.community([obj.get('subject_identifier')])
                bhs_subject.registration_datetime = tz.localize(parser.parse(obj.get('consent_datetime')))
                bhs_subject.data_sources = self.data_sources([bhs_subject.data_sources, 'edc'])
                bhs_subject.save()
                if request.json()['meta']['next']:
                    next_url = '{}{}'.format(self.host, request.json()['meta']['next'])
                sys.stdout.write('{0} of {1}. {2} added    \r'.format(n, total, added))
                sys.stdout.flush()

    def add_or_update_htc_subject(self):
        pass

    def add_or_update_clinic_subject(self):
        pass

    def add_or_update_smc_subject(self):
        pass

    def gender(self, key):
        options = {'M': 'M', 'F': 'F'}
        return options.get(key) or key

    def age(self, born, reference_date=None):
        reference_date = reference_date if reference_date is not None else date.today()
        born = parser.parse(str(born))
        reference_date = parser.parse(str(reference_date))
        return relativedelta(reference_date, born).years

    def citizen(self, key):
        key = str(key)
        options = {'True': True, 'False': False, 'Yes': True, 'No': False}
        return options.get(key) or key

    def community(self, identifiers):
        """Returns a community code """
        communities = []
        for identifier in identifiers:
            if re.match(HTC_PATTERN, identifier):
                communities.append(htc.get(identifier[3:5]))
            elif re.match(BHS_PATTERN, identifier):
                communities.append(bhs.get(identifier[4:6]))
            elif re.match(CLINIC_PATTERN, identifier):
                communities.append(clinic.get(identifier[1:3]))
            else:
                communities.append(identifier)
        communities = list(set(communities))
        return ','.join(communities)

    def data_sources(self, sources):
        sources = list(set([s for s in sources if s is not None]))
        return ','.join(sources)

    def result_as_decimal(self, value):
        try:
            return Decimal(value)
        except (InvalidOperation, TypeError):
            return None
