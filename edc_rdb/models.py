from django.db import models
from django.utils import timezone


class BaseModel(models.Model):

    created = models.DateTimeField(
        default=timezone.now)

    updated = models.DateTimeField(
        default=timezone.now)

    data_sources = models.CharField(
        max_length=50,
        null=True,
        help_text='list of data sources for this subject',
    )

    class Meta:
        abstract = True


class HivStatus(BaseModel):

    status = models.CharField(
        max_length=25,
        null=True,
    )

    status_date = models.DateField(
        null=True,
    )


class ArtStatus(BaseModel):

    status = models.CharField(
        max_length=25,
        null=True,
    )

    status_date = models.DateField(
        null=True,
    )


class LabHistory(BaseModel):

    sample_identifier = models.CharField(
        max_length=50,
        null=True)

    sample_date = models.DateField()

    order_identifier = models.CharField(
        max_length=50,
        null=True)

    status = models.CharField(
        max_length=50,
        null=True)

    test_name = models.CharField(
        max_length=50,
        null=True)

    result = models.CharField(
        max_length=50,
        null=True)

    result_dec = models.DecimalField(
        max_digits=24,
        decimal_places=3,
        null=True,
        help_text='result as decimal, if applicable')

    result_qualifier = models.CharField(
        max_length=10,
        null=True)

    result_datetime = models.DateTimeField(
        null=True)

    laboratory = models.CharField(
        max_length=50,
        null=True)

    source = models.CharField(
        max_length=50,
        null=True)

    class Meta:
        abstract = True


class BaseSubject(BaseModel):

    omang = models.CharField(
        max_length=25,
        null=True)

    omang_hash = models.TextField(
        max_length=1000,
        null=True)

    identifier = models.CharField(
        max_length=50,
        unique=True)

    registration_datetime = models.DateTimeField(
        null=True)

    gender = models.CharField(
        max_length=50)

    dob = models.DateField(
        null=True)

    age = models.IntegerField(
        null=True)

    citizen = models.CharField(
        max_length=50,
        null=True)

    hiv_status = models.CharField(
        max_length=25,
        null=True,
        help_text='SubjectReferral.hiv_result'
    )

    hiv_status = models.ForeignKey(
        to=HivStatus,
        null=True,
    )

    art_status = models.ForeignKey(
        to=ArtStatus,
        null=True,
    )

    community_name = models.CharField(
        max_length=50,
        null=True)

    services = models.CharField(
        max_length=10,
        null=True,
        help_text='list of services accessed')

    class Meta:
        abstract = True


class BhsSubject(BaseSubject):

    referred = models.NullBooleanField(
        help_text='SubjectReferral.subject_referred'
    )

    referral_code = models.CharField(
        max_length=25,
        null=True,
        help_text='SubjectReferral.referral_code'
    )

    referral_appt_date = models.DateField(
        null=True,
        help_text='SubjectReferral.referral_appt_date'
    )

    referral_hiv_result = models.CharField(
        max_length=25,
        null=True,
        help_text='SubjectReferral.hiv_result'
    )

    referral_new_pos = models.NullBooleanField(
        null=True,
        help_text='SubjectReferral.new_pos'
    )

    referral_on_art = models.NullBooleanField(
        null=True
    )

    referral_vl_drawn = models.NullBooleanField(
        null=True,
        help_text='from SubjectRequisition. True if a viral load sample was drawn in the household',
    )

    referral_vl_datetime = models.DateTimeField(
        null=True,
        help_text='from SubjectRequisition. Datetime of viral load drawn.',
    )

    class Meta:
        app_label = 'edc_rdb'


class BhsLabHistory(LabHistory):

    subject = models.ForeignKey(BhsSubject)

    class Meta:
        app_label = 'edc_rdb'
        unique_together = ('order_identifier', 'sample_date', 'status')


class HtcSubject(BaseSubject):

    class Meta:
        app_label = 'edc_rdb'


class HtcLabHistory(LabHistory):

    subject = models.ForeignKey(HtcSubject)

    class Meta:
        app_label = 'edc_rdb'


class SmcSubject(BaseSubject):

    class Meta:
        app_label = 'edc_rdb'


class SmcLabHistory(LabHistory):

    subject = models.ForeignKey(SmcSubject)

    class Meta:
        app_label = 'edc_rdb'


class ClinicSubject(BaseSubject):

    class Meta:
        app_label = 'edc_rdb'


class ClinicLabHistory(LabHistory):

    subject = models.ForeignKey(ClinicSubject)

    class Meta:
        app_label = 'edc_rdb'


class Subject(BaseModel):

    study_participant = models.IntegerField(
        null=True)

    omang = models.CharField(
        max_length=25,
        null=True)

    omang_hash = models.TextField(
        max_length=1000,
        null=True)

    bhs_identifier = models.CharField(
        max_length=50,
        null=True)

    htc_identifier = models.CharField(
        max_length=50,
        null=True)

    ccc_identifier = models.CharField(
        max_length=50,
        null=True)

    ecc_identifier = models.CharField(
        max_length=50,
        null=True)

    clinic_identifier = models.CharField(
        max_length=50,
        null=True)

    smc_identifier = models.CharField(
        max_length=100,
        null=True)

    bhs_datetime = models.DateTimeField(
        null=True)

    htc_datetime = models.DateTimeField(
        null=True)

    clinic_datetime = models.DateTimeField(
        null=True)

    smc_datetime = models.DateTimeField(
        null=True)

    gender = models.CharField(
        max_length=50)

    dob = models.DateField(
        null=True)

    age = models.IntegerField(
        null=True)

    citizen = models.CharField(
        max_length=50,
        null=True)

    clinic = models.CharField(
        max_length=50,
        null=True)

    referred = models.CharField(
        max_length=10,
        null=True,
        help_text='SubjectReferral.subject_referred'
    )

    referral_code = models.CharField(
        max_length=25,
        null=True,
        help_text='SubjectReferral.referral_code'
    )

    referral_appt_date = models.DateField(
        null=True,
        help_text='SubjectReferral.referral_appt_date'
    )

    hiv_result = models.CharField(
        max_length=25,
        null=True,
        help_text='SubjectReferral.hiv_result'
    )

    community = models.CharField(
        max_length=25,
        null=True)

    bhs = models.NullBooleanField(null=True)
    htc = models.NullBooleanField(null=True)
    smc = models.NullBooleanField(null=True)
    ccc = models.NullBooleanField(null=True)
    ecc = models.NullBooleanField(null=True)
    ltc = models.NullBooleanField(null=True)

    bhs_rdb_audit = models.IntegerField(null=True)
    htc_rdb_audit = models.IntegerField(null=True)
    clinic_rdb_audit = models.IntegerField(null=True)
    smc_rdb_audit = models.IntegerField(null=True)
    ltc_rdb_audit = models.IntegerField(null=True)

    class Meta:
        app_label = 'edc_rdb'


class Result(BaseModel):

    subject = models.ForeignKey(Subject)

    sample_date = models.DateField()

    order_identifier = models.CharField(
        max_length=50,
        null=True)

    status = models.CharField(
        max_length=50,
        null=True)

    source = models.CharField(
        max_length=50,
        null=True)

    test_name = models.CharField(
        max_length=50,
        null=True)

    result = models.CharField(
        max_length=50,
        null=True)

    result_dec = models.DecimalField(
        max_digits=24,
        decimal_places=3,
        null=True,
        help_text='result as decimal, if applicable')

    result_qualifier = models.CharField(
        max_length=10,
        null=True)

    result_datetime = models.DateTimeField(
        null=True)

    class Meta:
        app_label = 'edc_rdb'


class PimsSummary(models.Model):

    subject_identifier = models.CharField(
        max_length=25)

    htc_identifier = models.CharField(
        max_length=25,
        null=True)

    clinic_identifier = models.CharField(
        max_length=25,
        null=True)

    smc_identifier = models.CharField(
        max_length=25,
        null=True)

    gender = models.CharField(
        max_length=25)

    dob = models.DateField(
        null=True)

    age = models.IntegerField(
        null=True)

    citizen = models.CharField(
        max_length=25,
        null=True)

    clinic = models.CharField(
        max_length=25,
        null=True)

    art_status = models.CharField(
        max_length=25,
        null=True)

    viral_load = models.CharField(
        max_length=25,
        null=True)

    errors = models.TextField(
        max_length=500,
        null=True)

    class Meta:
        app_label = 'edc_rdb'
