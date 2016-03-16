import sys

from django.core.exceptions import ObjectDoesNotExist

from bhp066.apps.bcpp_subject.models import HivResultDocumentation, HivCareAdherence, HivTestingHistory, HivTestReview

from .data_errors import documented_pos
from .status import Record


class Review:

    survey_slug = 'bcpp-year-1'
    subject_visits = None
    errorlog = {}
    log = {}

    def load(self):
        for index, d in enumerate(documented_pos):
            record = Record(*d)
            self.query(record, index)

    def query(self, record, index):
        hiv_test_reviews = HivTestReview.objects.filter(
            recorded_hiv_result=record.recorded_hiv_result)
        total = hiv_test_reviews.count()
        for i, obj in enumerate(hiv_test_reviews):
            sys.stdout.write("{}/{} {}\r".format(i, total, record))
            sys.stdout.flush()
            obj2, obj3, obj4 = None, None, None
            try:
                obj2 = HivResultDocumentation.objects.get(
                    subject_visit=obj.subject_visit,
                    result_recorded=record.result_recorded,
                    result_doc_type=record.result_doc_type)
            except ObjectDoesNotExist:
                pass
            try:
                obj3 = HivTestingHistory.objects.get(
                    subject_visit=obj.subject_visit,
                    other_record=record.result_doc_type)
            except ObjectDoesNotExist:
                pass
            try:
                obj4 = HivCareAdherence.objects.get(
                    subject_visit=obj.subject_visit,
                    arv_evidence=record.arv_evidence)
            except ObjectDoesNotExist:
                pass
            visit = str(obj.subject_visit)
            if obj2 and obj3 and obj4:
                print('hit')
                lst = self.errorlog.get(visit, [])
                lst.append((obj2, obj3, obj4))
                self.errorlog.update({visit: lst})
            else:
                lst = self.log.get(visit, [])
                lst.append((obj2, obj3, obj4))
                self.log.update({visit: lst})
