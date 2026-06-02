from django.contrib import admin
from .models import Tender, Bidder, ProcurementRecord


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ('tender_ref', 'title', 'status', 'budget_amount', 'closing_date', 'tenant')
    list_filter = ('status', 'publication_date', 'closing_date', 'tenant')
    search_fields = ('tender_ref', 'title', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Bidder)
class BidderAdmin(admin.ModelAdmin):
    list_display = ('bidder_name', 'tender', 'registration_number', 'is_qualified', 'tenant')
    list_filter = ('is_qualified', 'tender', 'tenant', 'created_at')
    search_fields = ('bidder_name', 'registration_number', 'email')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(ProcurementRecord)
class ProcurementRecordAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'bidder', 'record_type', 'amount', 'order_date', 'tenant')
    list_filter = ('record_type', 'order_date', 'tenant', 'created_at')
    search_fields = ('po_number', 'bidder__bidder_name')
    readonly_fields = ('id', 'created_at', 'updated_at')
