# engine/admin.py

from django.contrib import admin
from django.utils.html import format_html
from engine.models import (
    WorkflowTemplate, TenantWorkflowConfig,
    Agent, WorkflowRun, AgentRun,
    NodeRun, HumanAction, DecisionPoint, MemoryPayload
)


# ─── Workflow Template ────────────────────────────────────────────────────────
from django import forms as django_forms
import json


class WorkflowTemplateForm(django_forms.ModelForm):
    graph_json = django_forms.CharField(
        initial='{}',
        required=False,
        widget=django_forms.Textarea(attrs={'rows': 3}),
        help_text='Enter valid JSON. Default: {}'
    )

    def clean_graph_json(self):
        data = self.cleaned_data.get('graph_json', '')
        if not data or data.strip() == '':
            return {}
        try:
            return json.loads(data)
        except Exception:
            raise django_forms.ValidationError('Enter valid JSON.')

    class Meta:
        model  = WorkflowTemplate
        fields = '__all__'


@admin.register(WorkflowTemplate)
class WorkflowTemplateAdmin(admin.ModelAdmin):
    form          = WorkflowTemplateForm
    list_display  = ('code', 'version', 'name', 'sector', 'is_active', 'created_at')
    list_filter   = ('sector', 'is_active')
    search_fields = ('code', 'name')
    readonly_fields = ('created_at',)
    ordering      = ('code', '-version')


# ─── Agent ────────────────────────────────────────────────────────────────────

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display  = ('code', 'name', 'sector', 'workflow_template', 'is_active')
    list_filter   = ('sector', 'is_active')
    search_fields = ('code', 'name')
    readonly_fields = ('created_at',)


# ─── Workflow Run ─────────────────────────────────────────────────────────────

class NodeRunInline(admin.TabularInline):
    model      = NodeRun
    extra      = 0
    readonly_fields = ('id', 'node_code', 'status', 'duration_ms', 'retry_count',
                       'input_ref', 'output_ref', 'error', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class HumanActionInline(admin.TabularInline):
    model      = HumanAction
    extra      = 0
    readonly_fields = ('id', 'node_code', 'actor', 'action',
                       'reason_code', 'justification', 'timestamp')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(WorkflowRun)
class WorkflowRunAdmin(admin.ModelAdmin):
    list_display  = ('id', 'template', 'status_badge', 'tenant',
                     'template_version', 'created_at', 'completed_at')
    list_filter   = ('status', 'template__sector')
    search_fields = ('id', 'template__code', 'tenant__name')
    readonly_fields = ('id', 'template_version', 'graph_thread_id',
                       'created_at', 'started_at', 'completed_at')
    inlines       = [NodeRunInline, HumanActionInline]
    ordering      = ('-created_at',)

    def status_badge(self, obj):
        colours = {
            'pending':           '#6b7280',
            'running':           '#2563eb',
            'waiting_for_input': '#d97706',
            'completed':         '#16a34a',
            'failed':            '#dc2626',
            'compensating':      '#9333ea',
        }
        colour = colours.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:600">{}</span>',
            colour, obj.status.upper()
        )
    status_badge.short_description = 'Status'


# ─── Agent Run ────────────────────────────────────────────────────────────────

@admin.register(AgentRun)
class AgentRunAdmin(admin.ModelAdmin):
    list_display  = ('id', 'agent', 'status', 'triggered_by',
                     'tenant', 'started_at', 'completed_at')
    list_filter   = ('status', 'agent__sector')
    search_fields = ('id', 'agent__code', 'triggered_by')
    readonly_fields = ('id', 'input_hash', 'created_at', 'started_at', 'completed_at')
    ordering      = ('-created_at',)


# ─── Human Action ─────────────────────────────────────────────────────────────

@admin.register(HumanAction)
class HumanActionAdmin(admin.ModelAdmin):
    list_display  = ('id', 'workflow_run', 'node_code', 'actor',
                     'action_badge', 'reason_code', 'timestamp')
    list_filter   = ('action',)
    search_fields = ('actor', 'reason_code', 'workflow_run__id')
    readonly_fields = ('id', 'workflow_run', 'node_code', 'actor',
                       'action', 'reason_code', 'justification', 'timestamp')
    ordering      = ('-timestamp',)

    # Immutable — no add or delete from admin
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def action_badge(self, obj):
        colours = {
            'APPROVED':  '#16a34a',
            'REJECTED':  '#dc2626',
            'ESCALATED': '#d97706',
        }
        colour = colours.get(obj.action, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:600">{}</span>',
            colour, obj.action
        )
    action_badge.short_description = 'Action'


# ─── Decision Point ───────────────────────────────────────────────────────────

@admin.register(DecisionPoint)
class DecisionPointAdmin(admin.ModelAdmin):
    list_display  = ('id', 'workflow_run', 'node_code', 'created_at')
    search_fields = ('workflow_run__id', 'node_code')
    readonly_fields = ('id', 'workflow_run', 'node_code', 'options',
                       'selected', 'decision_basis', 'quality_signals', 'created_at')
    ordering      = ('-created_at',)

    def has_add_permission(self, request):
        return False


# ─── Memory Payload ───────────────────────────────────────────────────────────

@admin.register(MemoryPayload)
class MemoryPayloadAdmin(admin.ModelAdmin):
    list_display  = ('content_hash', 'pii_class', 'schema_version', 'created_at')
    list_filter   = ('pii_class',)
    search_fields = ('content_hash',)
    readonly_fields = ('content_hash', 'content', 'schema_version',
                       'pii_class', 'created_at')
    ordering      = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False