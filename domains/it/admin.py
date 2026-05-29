# domains/it/admin.py

from django.contrib import admin
from django.utils.html import format_html
from domains.it.models import ChangeRequest, Vendor, SoftwareLicense, Incident


@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    list_display  = ('title', 'affected_system', 'risk_badge',
                     'status_badge', 'submitted_by', 'tenant', 'created_at')
    list_filter   = ('risk_level', 'status')
    search_fields = ('title', 'affected_system', 'submitted_by')
    readonly_fields = ('id', 'ingestion_batch_id', 'created_at', 'updated_at')

    def risk_badge(self, obj):
        colours = {
            'low':      '#16a34a',
            'medium':   '#d97706',
            'high':     '#dc2626',
            'critical': '#7c3aed',
        }
        colour = colours.get(obj.risk_level, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:600">{}</span>',
            colour, obj.risk_level.upper()
        )
    risk_badge.short_description = 'Risk'

    def status_badge(self, obj):
        colours = {
            'draft':     '#6b7280',
            'submitted': '#2563eb',
            'approved':  '#16a34a',
            'rejected':  '#dc2626',
            'deployed':  '#7c3aed',
        }
        colour = colours.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:600">{}</span>',
            colour, obj.status.upper()
        )
    status_badge.short_description = 'Status'


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display  = ('name', 'service_type', 'contact_email', 'is_active', 'tenant')
    list_filter   = ('is_active',)
    search_fields = ('name', 'service_type')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(SoftwareLicense)
class SoftwareLicenseAdmin(admin.ModelAdmin):
    list_display  = ('product_name', 'vendor', 'seats', 'expiry_date', 'is_active')
    list_filter   = ('is_active',)
    search_fields = ('product_name', 'vendor__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering      = ['expiry_date']


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display  = ('title', 'severity', 'status', 'affected_system',
                     'reported_by', 'tenant', 'created_at')
    list_filter   = ('severity', 'status')
    search_fields = ('title', 'affected_system', 'reported_by')
    readonly_fields = ('id', 'created_at', 'updated_at')