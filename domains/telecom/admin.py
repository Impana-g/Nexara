from django.contrib import admin
from .models import Operator, SpectrumLicense, Subscriber


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ('operator_code', 'name', 'operator_type', 'hq_location', 'is_active', 'tenant')
    list_filter = ('operator_type', 'is_active', 'tenant', 'created_at')
    search_fields = ('operator_code', 'name', 'registration_number')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(SpectrumLicense)
class SpectrumLicenseAdmin(admin.ModelAdmin):
    list_display = ('license_ref', 'operator', 'band_type', 'bandwidth_mhz', 'expiry_date', 'tenant')
    list_filter = ('band_type', 'is_active', 'expiry_date', 'tenant')
    search_fields = ('license_ref', 'operator__name')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'operator', 'subscriber_type', 'name', 'is_active', 'tenant')
    list_filter = ('subscriber_type', 'is_active', 'operator', 'tenant')
    search_fields = ('phone_number', 'name', 'email')
    readonly_fields = ('id', 'created_at', 'updated_at')
