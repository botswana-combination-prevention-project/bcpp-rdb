from django.contrib import admin

from .models import Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = ('bhs_identifier', 'referral_code', 'htc_identifier', 'smc_identifier', 'gender')
    list_filter = ('gender', 'referral_appt_date', 'referral_code')
    search_fields = ('bhs_identifier', 'htc_identifier', 'smc_identifier')
