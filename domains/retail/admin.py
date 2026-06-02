from django.contrib import admin
from .models import Vendor, ReturnRequest, GSTRecord


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('vendor_ref', 'business_name', 'gst_number', 'verification_status', 'email', 'tenant')
    list_filter = ('verification_status', 'onboarded_date', 'tenant', 'created_at')
    search_fields = ('vendor_ref', 'business_name', 'registration_number', 'gst_number')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('return_ref', 'vendor', 'status', 'requested_date', 'refund_amount', 'tenant')
    list_filter = ('status', 'requested_date', 'tenant')
    search_fields = ('return_ref', 'vendor__business_name', 'order_reference')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(GSTRecord)
class GSTRecordAdmin(admin.ModelAdmin):
    list_display = ('invoice_ref', 'vendor', 'record_type', 'taxable_amount', 'gst_amount', 'tenant')
    list_filter = ('record_type', 'transaction_date', 'gst_rate_percent', 'tenant')
    search_fields = ('invoice_ref', 'vendor__business_name', 'hsn_code')
    readonly_fields = ('id', 'created_at', 'updated_at')
