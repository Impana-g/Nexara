from django.contrib import admin
from .models import Shipment, CustomsRecord, CargoItem


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('shipment_ref', 'origin', 'destination', 'status', 'shipped_date', 'tenant')
    list_filter = ('status', 'shipped_date', 'expected_delivery', 'tenant')
    search_fields = ('shipment_ref', 'origin', 'destination')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(CustomsRecord)
class CustomsRecordAdmin(admin.ModelAdmin):
    list_display = ('customs_ref', 'shipment', 'clearance_status', 'clearance_date', 'duty_paid_amount', 'tenant')
    list_filter = ('clearance_status', 'clearance_date', 'tenant')
    search_fields = ('customs_ref', 'shipment__shipment_ref')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(CargoItem)
class CargoItemAdmin(admin.ModelAdmin):
    list_display = ('item_code', 'shipment', 'description', 'quantity', 'weight_kg', 'tenant')
    list_filter = ('tenant', 'created_at')
    search_fields = ('item_code', 'description', 'hs_code', 'shipment__shipment_ref')
    readonly_fields = ('id', 'created_at', 'updated_at')
