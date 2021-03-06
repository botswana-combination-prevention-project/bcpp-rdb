from django.contrib import admin

from .models import StudyParticipant, BhsParticipant, HtcParticipant, PimsPatient, PimsHaartInitiation
from rdb.models import CdcLabResults


@admin.register(StudyParticipant)
class StudyParticipantAdmin(admin.ModelAdmin):

    list_display = ('bhs_identifier', 'htc_identifier', 'omang_hash')
    search_fields = ('bhs_identifier', 'htc_identifier', 'omang_hash')


@admin.register(BhsParticipant)
class BhsParticipantAdmin(admin.ModelAdmin):

    list_display = ('id', 'study_participant', 'bhs_identifier', 'omang_hash')
    search_fields = ('bhs_identifier', 'omang_hash',
                     'study_participant__study_participant',
                     'study_participant__bhs_identifier',
                     'study_participant__htc_identifier')


@admin.register(HtcParticipant)
class HtcParticipantAdmin(admin.ModelAdmin):

    list_display = ('id', 'htc_identifier', 'age', 'gender', 'omang_hash')
    search_fields = ('is', 'htc_identifier', 'omang_hash')


@admin.register(PimsPatient)
class PimsPatientAdmin(admin.ModelAdmin):

    list_display = ('id', 'clinic_name', 'dob', 'gender', 'omang_hash')
    list_filter = ('clinic_name', 'citizenship', )
    search_fields = ('study_participant', 'clinic_name', 'omang_hash')


@admin.register(PimsHaartInitiation)
class PimsHaartInitiationAdmin(admin.ModelAdmin):
    list_display = ('id', 'study_participant', 'clinic_name', 'baseline_cd4', 'haart_regimen')
    list_filter = ('clinic_name', )
    search_fields = ('id', 'study_participant')


@admin.register(CdcLabResults)
class CdcLabResultsAdmin(admin.ModelAdmin):
    list_display = ('id', 'clinic_identifier', 'other_identifier', 'visit_datetime',
                    'cd4_result', 'vl_result', 'community')
    list_filter = ('community', 'visit_datetime')
    search_fields = ('id', 'clinic_identifier', 'other_identifier')
