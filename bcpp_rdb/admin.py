from django.contrib import admin

from .models import Subject, FileFormat, ImportHistory


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = ('bhs_identifier', 'referral_code', 'htc_identifier', 'smc_identifier', 'gender')
    list_filter = ('gender', 'referral_appt_date', 'referral_code')
    search_fields = ('bhs_identifier', 'htc_identifier', 'smc_identifier')


@admin.register(ImportHistory)
class ImportHistoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'filename', 'status', 'records', 'source', 'user', 'file_format')
    list_filter = ('status', 'user', 'source', 'file_format')
    search_fields = ('id', 'filename', )


@admin.register(FileFormat)
class FileFormatAdmin(admin.ModelAdmin):
    list_display = ('name', 'identity_field')
    list_filter = ('identity_field', )
    search_fields = ('header', )
