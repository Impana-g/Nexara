

# Register your models here.
# core/admin.py

from django.contrib import admin
from django.utils.html import format_html
from core.models import Tenant, TenantMembership


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display  = ('name', 'sector_badge', 'slug', 'is_active', 'created_at')
    list_filter   = ('sector', 'is_active')
    search_fields = ('name', 'slug')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering      = ('-created_at',)

    fieldsets = (
        ('Identity', {
            'fields': ('id', 'name', 'slug', 'sector')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def sector_badge(self, obj):
        colours = {
            'finance':       '#16a34a',
            'it':            '#2563eb',
            'hr':            '#9333ea',
            'legal':         '#b45309',
            'healthcare':    '#dc2626',
            'insurance':     '#0891b2',
            'education':     '#d97706',
            'government':    '#4b5563',
            'energy':        '#ca8a04',
            'telecom':       '#0284c7',
            'manufacturing': '#7c3aed',
            'logistics':     '#059669',
            'retail':        '#db2777',
            'cybersecurity': '#475569',
        }
        colour = colours.get(obj.sector, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:600">{}</span>',
            colour,
            obj.get_sector_display()
        )
    sector_badge.short_description = 'Sector'


@admin.register(TenantMembership)
class TenantMembershipAdmin(admin.ModelAdmin):
    list_display  = ('user', 'tenant', 'role', 'created_at')
    list_filter   = ('role', 'tenant__sector')
    search_fields = ('user__email', 'user__username', 'tenant__name')
    readonly_fields = ('created_at',)
    ordering      = ('-created_at',)