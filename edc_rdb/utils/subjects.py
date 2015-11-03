"""
find gender, age, dob, arv_naive
"""
import hashlib
import os
import pickle
import csv


from collections import namedtuple
from dateutil.relativedelta import relativedelta

from bhp066.apps.bcpp_subject.models import SubjectConsent

Subject = namedtuple('Subject', 'subject_identifier, omang, gender, age, omang_hash')


class Subjects:

    """A class that returns a subject dictionary with lookup info on each identifier.

    {subject_identifier, omang, gender, age, self.omang_hasher(omang)}"""

    def __init__(self, subject_identifiers_list):
        self.subjects = {}
        self.subject_identifiers = subject_identifiers_list

    def load(self):
        for subject_identifier in self.subject_identifiers:
            omang, gender, age = None, None, None
            try:
                subject_consent = SubjectConsent.objects.filter(
                    subject_identifier=subject_identifier).earliest('consent_datetime')
                omang = subject_consent.identity
                gender = subject_consent.gender
                age = relativedelta(subject_consent.consent_datetime, subject_consent.dob).years
            except SubjectConsent.DoesNotExist:
                subject_consent = None
            self.subjects[subject_identifier] = Subject(
                subject_identifier, omang, gender, age, self.omang_hasher(omang))

    def omang_hasher(self, omang):
        if omang:
            return hashlib.sha256(omang.encode()).hexdigest()
        else:
            return None

    def pickle(self, path):
        path = path or '~/nealia_subjects.pickle'
        with open(os.path.expanduser(path), 'wb') as f:
            pickle.dump(self.subjects, f)
