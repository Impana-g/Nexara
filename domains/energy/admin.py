from django.contrib import admin
from .models import ESGReport, EmissionRecord, CarbonCredit


@admin.register(ESGReport)
class ESGReportAdmin(admin.ModelAdmin):
    list_display = ('report_ref', 'report_type', 'reporting_period', 'published_date', 'tenant')
    list_filter = ('report_type', 'published_date', 'tenant', 'created_at')
    search_fields = ('report_ref', 'reporting_period')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(EmissionRecord)
class EmissionRecordAdmin(admin.ModelAdmin):
    list_display = ('emission_type', 'report', 'quantity_tonnes', 'measurement_date', 'tenant')
    list_filter = ('emission_type', 'measurement_date', 'tenant')
    search_fields = ('report__report_ref', 'source')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(CarbonCredit)
class CarbonCreditAdmin(admin.ModelAdmin):
    list_display = ('credit_ref', 'quantity_tonnes', 'status', 'issue_date', 'tenant')
    list_filter = ('status', 'issue_date', 'tenant', 'created_at')
    search_fields = ('credit_ref', 'project_name')
    readonly_fields = ('id', 'created_at', 'updated_at')
