from django.db import models


class SubjectConsent(models.Model):

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
    )

    gender = models.CharField(
        verbose_name="Gender",
        max_length=100,
        null=True,
    )

    identity = models.CharField(
        max_length=100,
        null=True,
    )

    dob = models.DateField(
        verbose_name="Date of birth",
        null=True,
    )

    gender = models.CharField(
        verbose_name="Gender",
        max_length=1,
        null=True,
    )

    citizen = models.CharField(
        verbose_name="Are you a Botswana citizen? ",
        max_length=3,
    )

    consent_datetime = models.DateTimeField(
        verbose_name="Consent date and time",
    )

    may_store_samples = models.CharField(
        verbose_name="Sample storage",
        max_length=3,
    )

    community = models.CharField(max_length=25, null=True)

    # survey = models.ForeignKey(Survey, editable=False)

    class Meta:
        managed = False
        app_label = 'bcpp'
        db_table = 'bcpp_subject_subjectconsent'


class SubjectReferral(models.Model):

    subject_identifier = models.CharField(
        max_length=25,
        db_column='subject_identifier'
    )

    referred = models.CharField(
        max_length=10,
        null=True,
        db_column='subject_referred'
    )

    referral_code = models.CharField(
        max_length=25,
        null=True,
        db_column='referral_code'
    )

    referral_appt_date = models.DateField(
        null=True,
        db_column='referral_appt_date'
    )

    hiv_result = models.CharField(
        max_length=25,
        null=True,
        db_column='hiv_result'
    )

    class Meta:
        managed = False
        app_label = 'bcpp'
        db_table = 'bcpp_subject_subjectreferral'
