from django.db import models
from django.utils import timezone


class PimsSummary(models.Model):

    subject_identifier = models.CharField(
        max_length=25)

    htc_identifier = models.CharField(
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
