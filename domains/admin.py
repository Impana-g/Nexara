# domains/admin.py

from django.contrib import admin
from django.utils.html import format_html
from domains.models import Client, Instrument, Portfolio, Holding, Transaction


# ─── Client ───────────────────────────────────────────────────────────────────

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display  = ('full_name', 'email', 'risk_badge', 'risk_tolerance', 'is_active', 'tenant')
    list_filter   = ('risk_profile', 'is_active')
    search_fields = ('full_name', 'email')
    readonly_fields = ('id', 'created_at', 'updated_at')

    def risk_badge(self, obj):
        colours = {
            'conservative': '#16a34a',
            'moderate':     '#d97706',
            'aggressive':   '#dc2626',
        }
        colour = colours.get(obj.risk_profile, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:600">{}</span>',
            colour, obj.risk_profile.upper()
        )
    risk_badge.short_description = 'Risk Profile'


# ─── Instrument ───────────────────────────────────────────────────────────────

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display  = ('ticker', 'name', 'asset_class', 'risk_score', 'currency', 'is_active')
    list_filter   = ('asset_class', 'currency', 'is_active')
    search_fields = ('ticker', 'name', 'instrument_uid')
    readonly_fields = ('created_at', 'updated_at')


# ─── Holding Inline ───────────────────────────────────────────────────────────

class HoldingInline(admin.TabularInline):
    model   = Holding
    extra   = 0
    readonly_fields = ('id', 'market_value_display', 'unrealised_pnl_display',
                       'ingestion_batch_id', 'created_at')
    fields  = ('instrument', 'quantity', 'average_cost', 'current_price',
               'market_value_display', 'unrealised_pnl_display', 'ingestion_batch_id')

    def market_value_display(self, obj):
        return f'{obj.market_value:,.2f}'
    market_value_display.short_description = 'Market Value'

    def unrealised_pnl_display(self, obj):
        pnl    = obj.unrealised_pnl
        colour = '#16a34a' if pnl >= 0 else '#dc2626'
        return format_html(
            '<span style="color:{};font-weight:600">{:+,.2f}</span>',
            colour, pnl
        )
    unrealised_pnl_display.short_description = 'Unrealised P&L'


# ─── Portfolio ────────────────────────────────────────────────────────────────

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display    = ('name', 'client', 'tenant', 'is_active', 'created_at')
    list_filter     = ('is_active',)
    search_fields   = ('name', 'client__full_name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines         = [HoldingInline]


# ─── Holding ──────────────────────────────────────────────────────────────────

@admin.register(Holding)
class HoldingAdmin(admin.ModelAdmin):
    list_display    = ('instrument', 'portfolio', 'quantity',
                       'current_price', 'market_value_display', 'pnl_display')
    search_fields   = ('instrument__ticker', 'portfolio__name')
    readonly_fields = ('id', 'ingestion_batch_id', 'created_at', 'updated_at')

    def market_value_display(self, obj):
        return f'{obj.market_value:,.2f}'
    market_value_display.short_description = 'Market Value'

    def pnl_display(self, obj):
        pnl    = obj.unrealised_pnl
        colour = '#16a34a' if pnl >= 0 else '#dc2626'
        return format_html(
            '<span style="color:{};font-weight:600">{:+,.2f}</span>',
            colour, pnl
        )
    pnl_display.short_description = 'Unrealised P&L'


# ─── Transaction ──────────────────────────────────────────────────────────────

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display    = ('tx_type', 'instrument', 'portfolio',
                       'quantity', 'price', 'total_value', 'tx_date')
    list_filter     = ('tx_type',)
    search_fields   = ('instrument__ticker', 'portfolio__name')
    readonly_fields = ('id', 'ingestion_batch_id', 'created_at', 'updated_at')
    ordering        = ('-tx_date', '-created_at')

    # Append-only — no editing or deleting from admin
    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False