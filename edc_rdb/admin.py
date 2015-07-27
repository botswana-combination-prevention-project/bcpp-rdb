from django.contrib import admin

from .models import Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = ('bhs_identifier', 'htc_identifier', 'smc_identifier', 'gender', 'omang_hash')
    list_filter = ('gender', )
    search_fields = ('bhs_identifier', 'htc_identifier', 'smc_identifier')
