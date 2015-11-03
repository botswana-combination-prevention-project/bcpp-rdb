from django.db import models


class StudyParticipant(models.Model):

    id = models.IntegerField(
        primary_key=True,
        db_column='dimcommonstudyparticipantkey'
    )

    omang_hash = models.CharField(
        max_length=100,
        null=True,
        db_column='omangnumber')

    bhs_identifier = models.CharField(
        max_length=25,
        db_column='bhssubjectid')

    htc_identifier = models.CharField(
        max_length=25,
        db_column='htcid')

    def __str__(self):
        return '({})'.format(', '.join((self.bhs_identifier, self.htc_identifier, str(self.id))))

    class Meta:
        app_label = 'rdb'
        db_table = 'dimcommonstudyparticipant'


class BhsParticipant(models.Model):

    id = models.IntegerField(
        primary_key=True,
        db_column='export_uuid')

    study_participant = models.ForeignKey(
        to=StudyParticipant,
        db_column='dimcommonstudyparticipantkey'
    )

    bhs_identifier = models.CharField(
        max_length=25,
        db_column='subject_identifier')

    omang_hash = models.CharField(
        max_length=36,
        null=True,
        db_column='omang')

    def __str__(self):
        return self.bhs_identifier

    class Meta:
        app_label = 'rdb'
        db_table = 'bhssubject_temp'


class HtcParticipant(models.Model):

    id = models.BigIntegerField(
        primary_key=True,
        db_column='dimcurrentstudyparticipantkey')

    htc_identifier = models.CharField(
        max_length=25,
        db_column='htcid')

    omang_hash = models.CharField(
        max_length=36,
        null=True,
        db_column='omangnumber')

    age = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        db_column='rdbcalculatedage')

    gender = models.CharField(
        max_length=15,
        null=True)

    def __str__(self):
        return self.htc_identifier

    class Meta:
        app_label = 'rdb'
        db_table = 'dimcurrentstudyparticipant'


class PimsPatient(models.Model):

    id = models.IntegerField(
        primary_key=True,
        db_column='dimcurrentpimspatientkey')

    omang_hash = models.TextField(
        max_length=1000,
        db_column='idno')

    gender = models.CharField(
        max_length=3,
        null=True)

    dob = models.DateTimeField(
        null=True)

    clinic_name = models.CharField(
        max_length=25,
        null=True,
        db_column='pimsclinicname',
    )

    citizenship = models.CharField(
        max_length=25,
        null=True,
    )

    clinical_stage_id = models.IntegerField(
        null=True,
        db_column='currentclinicalstageid'
    )

    registration_id = models.IntegerField(
        null=True,
        db_column='latestregistrationid'
    )

    regimen_id = models.IntegerField(
        null=True,
        db_column='currentregimenid'
    )

    def __str__(self):
        return str(self.id)

    class Meta:
        app_label = 'rdb'
        db_table = 'dimcurrentpimspatient'


class PimsHaartRegimen(models.Model):

    id = models.IntegerField(
        primary_key=True,
        db_column='dimpimshaartinitiationkey')

    regimen_line = models.CharField(
        max_length=25,
        null=True,
        db_column='regimenline')

    regimen = models.CharField(
        max_length=100,
        null=True,
        db_column='regimen')

    program = models.CharField(
        max_length=25,
        null=True,
        db_column='txprogram')

    def __str__(self):
        return '{} ({})'.format(self.regimen, self.regimen_line)

    class Meta:
        app_label = 'rdb'
        db_table = 'dimpimshaartinitiation'


class PimsHaartInitiation(models.Model):

    id = models.IntegerField(
        primary_key=True,
        db_column='factpimshaartinitiationkey')

    study_participant = models.ForeignKey(
        to=StudyParticipant,
        db_column='dimcommonstudyparticipantkey'
    )

    haart_regimen = models.ForeignKey(
        to=PimsHaartRegimen,
        to_field='id',
        db_column='dimpimshaartinitiationkey',
    )

    pims_patient = models.ForeignKey(
        to=PimsPatient,
        to_field='id',
        db_column='dimpimspatientkey')

    clinic_name = models.CharField(
        max_length=25,
        null=True,
        db_column='pimsclinicname')

    baseline_cd4 = models.IntegerField(
        null=True,
        db_column='baselinecd4count')

    class Meta:
        app_label = 'rdb'
        db_table = 'factpimshaartinitiation'


class PimsHaartRegistration(models.Model):

    id = models.IntegerField(
        primary_key=True,
        db_column='factpimsartpatientregistrationkey')

    study_participant = models.ForeignKey(
        to=StudyParticipant,
        db_column='dimcommonstudyparticipantkey'
    )

    pims_patient = models.ForeignKey(
        to=PimsPatient,
        to_field='id',
        db_column='dimpimspatientkey')

    registration_date = models.DateField(
        null=True,
        db_column='regdatekey')

    sourcesystempatientregistrationid = models.IntegerField(blank=True, null=True)
    dimclinickey = models.BigIntegerField(blank=True, null=True)

    class Meta:
        app_label = 'rdb'
        db_table = 'factpimsartpatientregistration'
        unique_together = (('dimclinickey', 'sourcesystempatientregistrationid'),)


class CdcLabResults(models.Model):

    id = models.IntegerField(
        primary_key=True,
        db_column='event_crf_id')

    clinic_identifier = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        db_column='ssid')

    other_identifier = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        db_column='oc_study_id')

    cd4_requisition_datetime = models.DateTimeField(
        blank=True,
        null=True,
        db_column='cd4vl_cd4dt')

    cd4_result_datetime = models.DateTimeField(
        blank=True,
        null=True,
        db_column='cd4vl_cd4rsltdt')

    cd4_result = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        db_column='cd4vl_cd4rslt')

    vl_requisition_datetime = models.DateTimeField(
        blank=True,
        null=True,
        db_column='cd4vl_vldt')

    vl_result_datetime = models.DateTimeField(
        blank=True,
        null=True,
        db_column='cd4vl_vlrsltdt')

    vl_result = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        db_column='cd4vl_vlrsltcpies')

    visit_datetime = models.DateTimeField(
        blank=True,
        null=True,
        db_column='visit_date')

    event_name = models.CharField(
        max_length=25,
        blank=True,
        null=True)
    community = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        db_column='study_name')

    crf_name = models.CharField(max_length=25, blank=True, null=True)

    date_created = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        app_label = 'rdb'
        db_table = 'oc_crf_pims2_dcf_lab'


class SmcParticipant(models.Model):

    id = models.BigIntegerField(
        primary_key=True,
        db_column='dimsmcstudyparticipantkey')

    omang_hash = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_column='omangnumber')

    participant_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_column='htcid',
        help_text='Could be bhs, htc or nothing')

    mergeid = models.CharField(max_length=50, blank=True, null=True)

    passportnumber = models.CharField(max_length=50, blank=True, null=True)

    dateofbirth = models.CharField(max_length=50, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    noage = models.CharField(max_length=50, blank=True, null=True)
    effectivestartdate = models.DateTimeField(blank=True, null=True)
    effectiveenddate = models.DateTimeField(blank=True, null=True)
    rowversion = models.IntegerField(blank=True, null=True)
    iscurrent = models.NullBooleanField()
    createdate = models.DateTimeField(blank=True, null=True)
    createuser = models.CharField(max_length=50, blank=True, null=True)
    lastupdatedate = models.DateTimeField(blank=True, null=True)
    lastupdateuser = models.CharField(max_length=50, blank=True, null=True)
    dimauditkey = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dimsmcstudyparticipant'


class EnrollmentCcc(models.Model):

    event_id = models.IntegerField(
        primary_key=True
    )

    event_crf_id = models.IntegerField(blank=True, null=True)

    date_created = models.DateTimeField(blank=True, null=True)

    date_updated = models.DateTimeField(blank=True, null=True)

    clinic_identifier = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_column='ssid')

    bhs_identifier = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        db_column='oc_study_id')

    appt_date = models.DateTimeField(
        blank=True,
        null=True)

    study_identifier = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_column='study_indentifier')

    class Meta:
        managed = False
        db_table = 'oc_crf_ccc_enrollment'


class EnrollmentEcc(models.Model):

    event_id = models.IntegerField(
        primary_key=True
    )

    event_crf_id = models.IntegerField(blank=True, null=True)

    date_created = models.DateTimeField(blank=True, null=True)

    date_updated = models.DateTimeField(blank=True, null=True)

    clinic_identifier = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_column='ssid')

    bhs_identifier = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        db_column='oc_study_id')

    appt_date = models.DateTimeField(
        blank=True,
        null=True)

    study_identifier = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_column='study_indentifier')

    class Meta:
        managed = False
        db_table = 'oc_crf_etc_enrollment'


class EnrollmentLossCc(models.Model):

    event_id = models.IntegerField(
        primary_key=True
    )

    event_crf_id = models.IntegerField(blank=True, null=True)

    date_created = models.DateTimeField(blank=True, null=True)

    date_updated = models.DateTimeField(blank=True, null=True)

    clinic_identifier = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_column='ssid')

    bhs_identifier = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        db_column='oc_study_id')

    appt_date = models.DateTimeField(
        blank=True,
        null=True)

    study_identifier = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_column='study_indentifier')

    class Meta:
        managed = False
        db_table = 'oc_crf_refusal'


class LabTest(models.Model):

    id = models.BigIntegerField(
        primary_key=True,
        db_column='dimcurrentpimslabtestkey'
    )

    clinic_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_column='pimsclinicname'
    )

    test_name = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        db_column='labtest'
    )

    labtestunit = models.CharField(
        max_length=50, blank=True, null=True
    )

    standardunit = models.IntegerField(
        blank=True, null=True
    )

    effectivestartdate = models.DateTimeField(blank=True, null=True)
    effectiveenddate = models.DateTimeField(blank=True, null=True)
    rowversion = models.IntegerField(blank=True, null=True)
    iscurrent = models.NullBooleanField()
    createdate = models.DateTimeField(blank=True, null=True)
    createuser = models.CharField(max_length=50, blank=True, null=True)
    lastupdatedate = models.DateTimeField(blank=True, null=True)
    lastupdateuser = models.CharField(max_length=50, blank=True, null=True)
    dimauditkey = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dimcurrentpimslabtest'


class PimsOrder(models.Model):
    """PIMS laboratory test orders and the order status."""

    id = models.BigIntegerField(
        primary_key=True,
        db_column='dimcurrentpimslaborderprofilekey'
    )

    clinic_name = models.CharField(
        max_length=50, blank=True, null=True,
        db_column='pimsclinicname'
    )

    order_identifier = models.IntegerField(
        blank=True,
        null=True,
        db_column='laborderno'
    )

    order_datetime = models.DateTimeField(
        blank=True,
        null=True,
        db_column='laborderdate')

    test_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_column='labprofile'
    )

    sample_datetime = models.DateTimeField(
        blank=True,
        null=True,
        db_column='sampledate',
    )

    status = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_column='testoutcome'
    )

    testing_facility = models.CharField(
        max_length=50, blank=True, null=True, db_column='testingfacility'
    )

    external_specimen_no = models.CharField(
        max_length=50, blank=True, null=True, db_column='externalspecimenno'
    )

    testingfacilityid = models.IntegerField(blank=True, null=True)
    effectivestartdate = models.DateTimeField(blank=True, null=True)
    effectiveenddate = models.DateTimeField(blank=True, null=True)
    rowversion = models.IntegerField(blank=True, null=True)
    iscurrent = models.NullBooleanField()
    createdate = models.DateTimeField(blank=True, null=True)
    createuser = models.CharField(max_length=50, blank=True, null=True)
    lastupdatedate = models.DateTimeField(blank=True, null=True)
    lastupdateuser = models.CharField(max_length=50, blank=True, null=True)
    dimauditkey = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dimcurrentpimslaborderprofile'


class PimsLab(models.Model):

    id = models.BigIntegerField(
        primary_key=True,
        db_column='factpimslaborderprofiletestkey'
    )

    pims_order = models.ForeignKey(
        to=PimsOrder,
        db_column='dimcurrentpimslaborderprofilekey'
    )

    study_participant = models.ForeignKey(
        to=StudyParticipant,
        db_column='dimcommonstudyparticipantkey'
    )

    pims_patient = models.ForeignKey(
        to=PimsPatient,
        db_column='dimcurrentpimspatientkey')

    sample_datekey = models.IntegerField(
        blank=True,
        null=True,
        db_column='sampledatekey'
    )

    specimen_datekey = models.IntegerField(
        blank=True,
        null=True,
        db_column='specimendatekey'
    )

    result_datekey = models.IntegerField(
        blank=True,
        null=True,
        db_column='resultdatekey'
    )

    result_qualifier = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        db_column='resultqualifier'
    )

    result = models.DecimalField(
        max_digits=24,
        decimal_places=3,
        blank=True,
        null=True
    )

    sourcesystemlaborderprofiletestid = models.IntegerField(blank=True, null=True)
    dimclinickey = models.BigIntegerField(blank=True, null=True)
    effectivestartdate = models.DateTimeField(blank=True, null=True)
    effectiveenddate = models.DateTimeField(blank=True, null=True)
    iscurrent = models.NullBooleanField()
    rowversion = models.IntegerField(blank=True, null=True)
    createdate = models.DateTimeField(blank=True, null=True)
    createuser = models.DateTimeField(blank=True, null=True)
    dimauditkey = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'factpimslaborderprofiletest'
        unique_together = (('dimclinickey', 'sourcesystemlaborderprofiletestid'),)
