from django.contrib import admin
from .models import Applicant, Program, Grant, AdmissionRecord


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('application_ref', 'first_name', 'last_name', 'email', 'gpa', 'tenant')
    list_filter = ('applied_date', 'tenant', 'created_at')
    search_fields = ('application_ref', 'first_name', 'last_name', 'email')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('program_code', 'name', 'level', 'seats', 'tenant')
    list_filter = ('level', 'is_active', 'tenant', 'created_at')
    search_fields = ('program_code', 'name')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    list_display = ('grant_ref', 'grant_type', 'amount', 'tenant')
    list_filter = ('grant_type', 'is_active', 'tenant', 'created_at')
    search_fields = ('grant_ref', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(AdmissionRecord)
class AdmissionRecordAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'program', 'decision_status', 'decision_date', 'tenant')
    list_filter = ('decision_status', 'decision_date', 'tenant')
    search_fields = ('applicant__application_ref', 'program__program_code')
    readonly_fields = ('id', 'created_at', 'updated_at')
