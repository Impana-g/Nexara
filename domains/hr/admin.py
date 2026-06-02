# domains/hr/admin.py

from django.contrib import admin
from .models import Employee, JobRequisition, OfferLetter, PayrollRecord


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'department', 'designation', 'employment_type', 'status', 'date_of_joining')
    list_filter = ('status', 'employment_type', 'department', 'created_at')
    search_fields = ('full_name', 'email', 'department', 'designation')
    ordering = ('full_name',)


@admin.register(JobRequisition)
class JobRequisitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'budget_min', 'budget_max', 'status', 'requested_by', 'created_at')
    list_filter = ('status', 'department', 'created_at')
    search_fields = ('title', 'department', 'requested_by')
    ordering = ('-created_at',)


@admin.register(OfferLetter)
class OfferLetterAdmin(admin.ModelAdmin):
    list_display = ('candidate_name', 'candidate_email', 'designation', 'department', 'offered_salary', 'status', 'created_at')
    list_filter = ('status', 'department', 'created_at')
    search_fields = ('candidate_name', 'candidate_email', 'designation', 'department')
    ordering = ('-created_at',)


@admin.register(PayrollRecord)
class PayrollRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'basic_salary', 'pf_deduction', 'esi_deduction', 'net_salary', 'is_exception')
    list_filter = ('month', 'is_exception', 'created_at')
    search_fields = ('employee__full_name', 'month')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-month',)
