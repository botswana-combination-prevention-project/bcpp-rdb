from copy import copy
from pprint import pprint
import itertools
from collections import namedtuple
from django.test import TestCase


POS = 'Pos'
NEG = 'Neg'
IND = 'Ind'
UNK = 'Unknown'
NO = 'No'
YES = 'Yes'
NA = 'N/A'
NONE = ''

Record = namedtuple('Record', 'recorded_hiv_result other_record result_recorded')


class TestStuff(TestCase):
    
# a. final_docd_pos = 1 if
# * recorded_hiv_result='POS'  OR
# * other_record="YES" and result_recorded does not equal "NEG"

    def run_method(self, fn, pp=None):
        pp = True if pp is None else pp
        self.data = []
        self.data_one = []
        self.data_zero = []
        self.data_none = []
        recorded_hiv_result_options = [POS, NEG, UNK, IND]
        other_record_options = [YES, NO, NA]
        result_recorded_options = [POS, NEG, UNK, IND, NONE]
        for r in itertools.product(
                recorded_hiv_result_options, other_record_options, result_recorded_options):
            self.data.append(r)
        for d in self.data:
            record = Record(*d)
            if fn(record) == 1:
                self.data_one.append(record)
            elif fn(record) == 0:
                self.data_zero.append(record)
            else:
                self.data_none.append(record)
        if pp:
            print('returns 1 ********************************')
            pprint(self.data_one)
            print('returns 0 ********************************')
            pprint(self.data_zero)
            print('returns None *****************************' )
            pprint(self.data_none)
        return copy(self.data_one), copy(self.data_zero), copy(self.data_none)

        """
        recorded_hiv_result = "What was the recorded HIV test result?",
            "If the participant and written record differ, the result"
            "from the written record should be recorded."

        other_record = "Do you have any other available documentation of positive HIV status?"

        result_recorded = 'What is the recorded HIV status indicated by this additional document?'
        """
    def documented_pos_kara(self, record):
        if record.recorded_hiv_result == POS or (record.other_record == YES and record.result_recorded != NEG):
            return 1
        elif (record.recorded_hiv_result not in [POS, NEG] and not
              (record.other_record == YES and record.result_recorded == POS)):
            return 0
        else:
            return None

    def documented_pos_erik(self, record):
        if record.recorded_hiv_result == POS:
            return 1
        elif record.other_record == YES and record.result_recorded == POS:
            return 1
        elif record.other_record == YES and record.result_recorded != POS:
            return 0
        else:
            return None

    def test_documented_pos_kara(self):
        self.run_method(self.documented_pos_kara)

    def test_documented_pos_erik(self):
        self.run_method(self.documented_pos_erik)

    def test_compare(self):
        kara1, kara0, kara = self.run_method(self.documented_pos_kara, pp=False)
        erik1, erik0, erik = self.run_method(self.documented_pos_erik, pp=False)
        print('Kara returns 1, erik does not')
        pprint([k for k in kara1 if k not in erik1])
        print('Erik returns 1, Kara does not')
        pprint([e for e in erik1 if e not in kara1])
        print('Kara returns 0, erik returns 1')
        pprint([k for k in kara0 if k in erik1])
        print('Erik returns 0, Kara returns 1')
        pprint([e for e in erik0 if e in kara1])

    def final_hiv_result(self, today_hiv_result, documented_pos):
        if today_hiv_result == POS:
            return 1
        elif today_hiv_result == NEG:
            return 0
        else:
            return documented_pos

    def test_today_hiv_result(self):
        self.assertEqual(1, self.final_hiv_result(POS, 1))
        self.assertEqual(1, self.final_hiv_result(POS, 0))
        self.assertEqual(0, self.final_hiv_result(NEG, 1))
        self.assertEqual(0, self.final_hiv_result(NEG, 0))
        self.assertEqual(1, self.final_hiv_result(IND, 1))
        self.assertEqual(0, self.final_hiv_result(IND, 0))
        self.assertEqual(1, self.final_hiv_result(UNK, 1))
        self.assertEqual(0, self.final_hiv_result(UNK, 0))
        self.assertEqual(NONE, self.final_hiv_result(UNK, NONE))
        self.assertEqual(NONE, self.final_hiv_result(IND, NONE))
