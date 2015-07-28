from django.db import models
from django.utils import timezone


class Subject(models.Model):

    omang = models.CharField(
        max_length=25,
        null=True)

    omang_hash = models.CharField(
        max_length=100,
        null=True)

    bhs_identifier = models.CharField(
        max_length=50,
        null=True)

    htc_identifier = models.CharField(
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

    bhs_rdb_audit = models.IntegerField(null=True)
    htc_rdb_audit = models.IntegerField(null=True)
    clinic_rdb_audit = models.IntegerField(null=True)
    smc_rdb_audit = models.IntegerField(null=True)
    ltc_rdb_audit = models.IntegerField(null=True)

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

    updated = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'edc_rdb'
