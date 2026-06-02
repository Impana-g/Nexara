from django.contrib import admin
from .models import Contract, Case, Filing, ConflictRecord


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_ref', 'title', 'status', 'tenant', 'start_date')
    list_filter = ('status', 'tenant', 'created_at')
    search_fields = ('contract_ref', 'title')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('case_ref', 'title', 'status', 'tenant', 'filing_date')
    list_filter = ('status', 'tenant', 'created_at')
    search_fields = ('case_ref', 'title')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Filing)
class FilingAdmin(admin.ModelAdmin):
    list_display = ('filing_type', 'case', 'filing_date', 'tenant')
    list_filter = ('filing_type', 'filing_date', 'tenant')
    search_fields = ('filing_type', 'case__case_ref')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(ConflictRecord)
class ConflictRecordAdmin(admin.ModelAdmin):
    list_display = ('conflict_ref', 'conflict_type', 'severity', 'tenant')
    list_filter = ('conflict_type', 'severity', 'tenant', 'created_at')
    search_fields = ('conflict_ref', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
