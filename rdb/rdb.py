import re
import requests
import sys

from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q

from edc_rdb.models import Subject

from .models import StudyParticipant
from .models import BhsParticipant, SmcParticipant

BHS_PATTERN = r'^066\-[0-9]{8}\-[0-9]{1}'
CLINIC_PATTERN = r'^[123]{1}[0-9]{2}\-[0-9]{4}'
HTC_PATTERN = r'^[0-9]{2}\-[0-9]{2}\-[0-9]{3}\-[0-9]{2}'


class Rdb(object):

    def __init__(self, edc_url=None, filter_options=None):
        self.edc_url = edc_url or 'http://localhost:8000/api/bcpp/'
        self.filter_options = filter_options or {}

    def fetch_study_participant(self):
        pass

    def study_participants(self):
        if self.filter_options:
            return StudyParticipant.objects.filter(**self.filter_options)
        else:
            StudyParticipant.objects.all()

    def fetch_subjects(self):
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
            subject.save(update_fields=['omang_hash', 'htc_identifier', 'bhs_identifier', 'clinic_identifier'])
        Subject.objects.filter(htc_identifier='').update(htc_identifier=None)
        Subject.objects.filter(bhs_identifier='').update(bhs_identifier=None)
        Subject.objects.filter(clinic_identifier='').update(clinic_identifier=None)

    def update_subjects(self):
        """Update subjects from the EDC."""
        n = 0
        updated = 0
        total = Subject.objects.filter(bhs_identifier__startswith='066').count()
        for subject in Subject.objects.filter(bhs_identifier__startswith='066'):
            n += 1
            if subject.bhs_identifier:
                r = requests.get(
                    '{}subject_consent/?format=json&subject_identifier={}'.format(
                        self.edc_url, subject.bhs_identifier))
                try:
                    subject.omang = r.json()['objects'][0]['identity']
                    subject.dob = r.json()['objects'][0]['dob']
                    subject.gender = r.json()['objects'][0]['gender']
                    subject.save(update_fields=['omang', 'dob', 'gender'])
                    updated += 1
                except (IndexError, KeyError):
                    pass
            sys.stdout.write('{0} of {1}. {2} updated    \r'.format(n, total, updated))
            sys.stdout.flush()

    def update_smc(self):
        n = 0
        for subject in Subject.objects.all():
            n += 1
            smc_identifier = self.smc_identifier(subject)
            if (subject.smc_identifier is not None and
                    subject.smc_identifier != smc_identifier):
                subject.save(update_fields=['smc_identifier'])
            sys.stdout.write('{0}  {1:100s}\r'.format(n, smc_identifier or ''))
            sys.stdout.flush()

    def identifier(self, identifier, result=None):
        result = result or {}
        if re.match(HTC_PATTERN, identifier):
            result.update({'htc_identifier': identifier})
        elif re.match(BHS_PATTERN, identifier):
            result.update({'bhs_identifier': identifier})
        elif re.match(CLINIC_PATTERN, identifier):
            result.update({'clinic_identifier': identifier})
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
