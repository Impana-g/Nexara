from django.contrib import admin
from .models import Policy, Claim, FraudFlag, Settlement


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('policy_number', 'policy_type', 'holder_name', 'premium_amount', 'tenant')
    list_filter = ('policy_type', 'is_active', 'tenant', 'start_date')
    search_fields = ('policy_number', 'holder_name')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_number', 'policy', 'claim_amount', 'status', 'tenant')
    list_filter = ('status', 'filed_date', 'tenant')
    search_fields = ('claim_number', 'policy__policy_number')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(FraudFlag)
class FraudFlagAdmin(admin.ModelAdmin):
    list_display = ('claim', 'severity', 'flagged_date', 'resolved_date', 'tenant')
    list_filter = ('severity', 'flagged_date', 'tenant')
    search_fields = ('claim__claim_number', 'flag_reason')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ('claim', 'settlement_amount', 'settled_date', 'tenant')
    list_filter = ('settled_date', 'tenant', 'created_at')
    search_fields = ('claim__claim_number', 'reference_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
