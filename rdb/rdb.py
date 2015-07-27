import re
import sys

from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q
from edc_rdb.models import Subject

from .models import StudyParticipant
from rdb.models import BhsParticipant, SmcParticipant

BHS_PATTERN = r'^066\-[0-9]{8}\-[0-9]{1}'
CLINIC_PATTERN = r'^[123]{1}[0-9]{2}\-[0-9]{4}'
HTC_PATTERN = r'^[0-9]{2}\-[0-9]{2}\-[0-9]{3}\-[0-9]{2}'


class Rdb(object):

    def update_subject(self):

        # check Oc

        # check htc
        for study_participant in StudyParticipant.objects.all():
            try:
                Subject.objects.get(
                    omang_hash=study_participant.omang_hash[0:100],
                )
            except Subject.DoesNotExist:
                print(study_participant.omang_hash)
                Subject.objects.create(
                    omang_hash=study_participant.omang_hash[0:100],
                    htc_identifier=self.htc_identifier(study_participant),
                    bhs_identifier=self.bhs_identifier(study_participant),
                    smc_identifier=None,
                )
#             if re.match(CLINIC_PATTERN, study_participant.clinic_identifier):
#                 subject.clinic_identifier = study_participant.clinic_identifier

    def update_smc(self):
        n = 0
        for subject in Subject.objects.all():
            n += 1
            smc_identifier = self.smc_identifier(subject)
            if (subject.smc_identifier is not None and
                    subject.smc_identifier != smc_identifier):
                subject.save()
            sys.stdout.write('{0}  {1:100s}\r'.format(n, smc_identifier or ''))
            sys.stdout.flush()

    def htc_identifier(self, study_participant):
        if re.match(HTC_PATTERN, study_participant.htc_identifier):
            return study_participant.htc_identifier[0:50]
        return None

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

    def bhs_identifier(self, study_participant):
        if re.match(BHS_PATTERN, study_participant.bhs_identifier):
            return study_participant.bhs_identifier[0:50]
        return None
