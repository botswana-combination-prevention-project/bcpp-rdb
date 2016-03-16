from edc_utils import ReviewDerivedVariables, NotHandledError 

from bhp066.apps.bcpp_subject.models import (
    HivTestReview, HivResultDocumentation, HivCareAdherence,
    HivTestingHistory, SubjectVisit, HivResult, ElisaHivResult)

DWTA = 'DWTA'
POS = 'POS'
NEG = 'NEG'
IND = 'IND'
UNK = 'UNKNOWN'
NO = 'No'
YES = 'Yes'
NA = 'N/A'
NONE = None
NAIVE = 'ARV Naive'
DEFAULTER = 'ARV Defaulter'
ON_ARV = 'On ARV'


HIV_DOC_TYPE = (
    ('Tebelopele', 'Tebelopele'),
    ('Lab result form', 'Lab result form'),
    ('ART Prescription', 'ART Prescription'),
    ('PMTCT Prescription', 'PMTCT Prescription'),
    ('Record of CD4 count', 'Record of CD4 count'),
    ('OTHER', 'Other OPD card or ANC card documentation'),
)


class BcppDerivationReview(ReviewDerivedVariables):
    """
    HivTestingHistory:
        has_record = "Is a record of last [most recent] HIV test [OPD card, Tebelopele,"
                     " other] available to review?" (triggers HivTestReview)
        verbal_hiv_result = "Please tell me the results of your last [most recent] HIV test?"
        other_record = "Do you have any other available documentation of positive HIV status?"
                        (triggers HivResultDocumentation)

    HivTestReview:
        recorded_hiv_result = "What was the recorded HIV test result?",
            "If the participant and written record differ, the result"
            "from the written record should be recorded."

    HivResultDocumentation:
        result_recorded = 'What is the recorded HIV status indicated by this additional document?'
        result_doc_type = "What is the type of document used?"

    HivCareAdherence:
        arv_evidence = "Is there evidence [OPD card, tablets, masa number] that the participant is on therapy?"
        (comment this question is mostly used to confirm a YES)
        ever_taken_arv = "Have you ever taken any antiretroviral therapy (ARVs) for your HIV infection?
            [For women: Do not include treatment that you took during pregnancy to protect
            your baby from HIV]"
        on_arv = "Are you currently taking antiretroviral therapy (ARVs)?"

    ElisaHivResult:
        hiv_result:
    """

    fields = [
        'hiv_result', 'today_hiv_result', 'recorded_hiv_result', 'other_record',
        'result_recorded', 'result_doc_type', 'arv_evidence', 'ever_taken_arv', 'on_arv']
    models = [ElisaHivResult, HivResult, HivResultDocumentation, HivTestingHistory, HivTestReview, HivCareAdherence]
    visit_model = SubjectVisit
    visit_model_filter = {'household_member__household_structure__survey__survey_slug': 'bcpp-year-1'}
    visit_model_exclude = {
        'household_member__household_structure__household__plot__community__in': ['nata', 'masunga']}

    opts_today_hiv_result = [POS, NEG, IND, NONE]
    opts_recorded_hiv_result = [POS, NEG, UNK, IND, NONE]
    opts_other_record = [YES, NO, NA, NONE]
    opts_result_recorded = [POS, NEG, UNK, IND, NONE]
    opts_arv_evidence = [YES, NO, NONE]
    opts_result_doc_type = [item[0] for item in HIV_DOC_TYPE] + [NONE]
    opts_ever_taken_arv = [YES, NO, DWTA, NONE]
    opts_on_arv = [YES, NO, DWTA, NONE]
    opts_hiv_result = [POS, NEG, NONE]

    def __init__(self, mode, verbose=None, **kwargs):
        self.mode = mode
        self.verbose = verbose if verbose is True else False
        super(BcppDerivationReview, self).__init__(**kwargs)

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self.mode, self.verbose)

    def elisa_hiv_result(self, record):
        return record.hiv_result

    def fn_art_exposed(self, record, subject_visit=None):
        if (record.ever_taken_arv == YES or record.on_arv == YES or self.fn_arv_evidence(record, subject_visit)):
            return True
        else:
            return False

    def fn_previous_result(self, record, subject_visit=None):
        """Returns the previous result or None.

            * if tested NEG by ELISA or in household today implies NEG previously
            * any documentation of positive status
            * any "documentation" of negative status
            * otherwise unknown
        """
        if self.elisa_hiv_result(record) == NEG:
            previous_result = NEG
        elif record.today_hiv_result == NEG:
            previous_result = NEG
        elif self.fn_documented_pos(record, subject_visit):
            previous_result = POS
        elif self.fn_documented_neg(record, subject_visit):
            previous_result = NEG
        else:
            previous_result = None
            print(previous_result, dict(record._asdict()))
        return previous_result

    def fn_previous_result_known(self, record, subject_visit=None):
        return True if self.fn_previous_result(record, subject_visit) else False

    def fn_final_arv_status(self, record, subject_visit=None):
        if self.fn_final_hiv_result(record, subject_visit) == POS:
            if record.ever_taken_arv in [NO, NONE, DWTA]:
                # naive
                if self.fn_arv_evidence(record, subject_visit):
                    print(record)
                    raise NotHandledError('1b')
                elif record.on_arv == YES:
                    print(record, self.fn_arv_evidence(record, subject_visit))
                    raise NotHandledError('1a')
                else:
                    final_arv_status = NAIVE
            elif (record.ever_taken_arv == YES or record.on_arv == YES or
                  self.fn_arv_evidence(record, subject_visit)):
                # on art
                if record.on_arv == NO:
                    final_arv_status = DEFAULTER
                elif record.on_arv == YES:
                    final_arv_status = ON_ARV
                elif self.fn_arv_evidence(record, subject_visit):
                    final_arv_status = ON_ARV
                else:
                    print(record)
                    raise NotHandledError('2')
        else:
            final_arv_status = None  # '.'
        return final_arv_status

    def fn_final_hiv_result(self, record, subject_visit=None):
        if self.elisa_hiv_result(record) == POS:  # elisa
            return POS
        elif self.elisa_hiv_result(record) == NEG:  # elisa
            return NEG
        elif record.today_hiv_result == POS:
            return POS
        elif record.today_hiv_result == NEG:
            return NEG
        else:
            return POS if self.fn_documented_pos(record, subject_visit) else None

    def fn_arv_evidence(self, record, subject_visit=None):
        """
        SAS:
            if index(upcase(EDC.result_doc_type),"ART PRESCRIPTION")>0 then der_arv_evidence='Yes';
                else der_arv_evidence=EDC.arv_evidence;
        """
        value = None
        if record.result_doc_type:
            if 'ART Prescription' in record.result_doc_type:
                value = True
            else:
                value = True if record.arv_evidence == YES else False
        return value

    def fn_documented_pos(self, record, subject_visit=None):
        documented_pos = None
        if (record.recorded_hiv_result == POS or record.result_recorded == POS or
                self.fn_arv_evidence(record, subject_visit)):
            documented_pos = True
        else:
            documented_pos = False
        return documented_pos

    def fn_documented_neg(self, record, subject_visit=None):
        """Returns True documents suggest NEG status after first confirming the documents do not confirm
        POS status."""
        documented_neg = None
        if self.fn_documented_pos(record, subject_visit):
            documented_neg = False
        elif ((record.recorded_hiv_result == NEG or record.result_recorded == NEG) and not
                self.fn_arv_evidence(record, subject_visit)):
            documented_neg = True
        else:
            documented_neg = False
        return documented_neg
