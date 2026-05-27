

# Create your models here.
# engine/models.py

import uuid
from django.db import models
from core.models import TenantAwareModel, Tenant


# ─── Workflow Template ────────────────────────────────────────────────────────

class WorkflowTemplate(models.Model):
    """
    Immutable blueprint for a workflow graph.
    Never updated in-place — a new version is created instead.
    Running workflows lock to a specific (code, version) at creation time.
    """
    code        = models.CharField(max_length=100)
    version     = models.IntegerField(default=1)
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sector      = models.CharField(max_length=50)        # which sector this belongs to
    graph_json  = models.JSONField(default=dict)         # LangGraph graph definition
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = 'workflow_templates'
        unique_together = ('code', 'version')
        ordering        = ['code', '-version']

    def __str__(self):
        return f'{self.code} v{self.version} ({self.sector})'


# ─── Tenant Workflow Config ───────────────────────────────────────────────────

class TenantWorkflowConfig(TenantAwareModel):
    """
    Per-tenant overrides for a workflow template.
    Allows a tenant to fork graph behaviour without changing the platform default.
    """
    template    = models.ForeignKey(WorkflowTemplate, on_delete=models.PROTECT)
    overrides   = models.JSONField(default=dict)         # node-level overrides
    is_active   = models.BooleanField(default=True)

    class Meta:
        db_table        = 'tenant_workflow_configs'
        unique_together = ('tenant', 'template')

    def __str__(self):
        return f'{self.tenant.name} → {self.template.code}'


# ─── Agent ────────────────────────────────────────────────────────────────────

class Agent(models.Model):
    """
    Named trigger for a workflow.
    e.g. market_data_sync, portfolio_import, change_request_approval
    """
    code            = models.CharField(max_length=100, unique=True)
    name            = models.CharField(max_length=255)
    description     = models.TextField(blank=True)
    sector          = models.CharField(max_length=50)
    workflow_template = models.ForeignKey(
        WorkflowTemplate, on_delete=models.PROTECT, related_name='agents'
    )
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'agents'

    def __str__(self):
        return f'{self.code} ({self.sector})'


# ─── Workflow Run ─────────────────────────────────────────────────────────────

class WorkflowRun(TenantAwareModel):
    """
    One execution instance of a WorkflowTemplate.
    Template version is locked at creation — running workflows
    never see template changes.
    """
    class Status(models.TextChoices):
        PENDING      = 'pending',           'Pending'
        RUNNING      = 'running',           'Running'
        WAITING      = 'waiting_for_input', 'Waiting for Input'
        COMPLETED    = 'completed',         'Completed'
        FAILED       = 'failed',            'Failed'
        COMPENSATING = 'compensating',      'Compensating'

    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent            = models.ForeignKey(Agent, on_delete=models.PROTECT, null=True, blank=True)
    template         = models.ForeignKey(WorkflowTemplate, on_delete=models.PROTECT)
    template_version = models.IntegerField()                 # locked at creation
    status           = models.CharField(
                           max_length=30,
                           choices=Status.choices,
                           default=Status.PENDING
                       )
    graph_thread_id  = models.CharField(max_length=255, null=True, blank=True)
    input_data       = models.JSONField(default=dict)        # trigger input
    output_data      = models.JSONField(default=dict)        # final output
    error_message    = models.TextField(blank=True)
    started_at       = models.DateTimeField(null=True, blank=True)
    completed_at     = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'workflow_runs'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.template.code} [{self.status}] {self.id}'


# ─── Agent Run ────────────────────────────────────────────────────────────────

class AgentRun(TenantAwareModel):
    """
    Primary audit record for each agent execution.
    Created at trigger time, updated at completion.
    """
    class Status(models.TextChoices):
        PENDING   = 'pending',   'Pending'
        RUNNING   = 'running',   'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED    = 'failed',    'Failed'

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent        = models.ForeignKey(Agent, on_delete=models.PROTECT)
    workflow_run = models.OneToOneField(WorkflowRun, on_delete=models.CASCADE, related_name='agent_run')
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    triggered_by = models.CharField(max_length=255)         # username or 'scheduler'
    input_hash   = models.CharField(max_length=64, blank=True)
    output_summary = models.JSONField(default=dict)
    started_at   = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'agent_runs'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.agent.code} [{self.status}] {self.id}'


# ─── Node Run ─────────────────────────────────────────────────────────────────

class NodeRun(models.Model):
    """
    Append-only record for each node execution within a WorkflowRun.
    Never updated — a retry creates a new NodeRun record.
    """
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_run = models.ForeignKey(WorkflowRun, on_delete=models.CASCADE, related_name='node_runs')
    node_code    = models.CharField(max_length=100)
    status       = models.CharField(max_length=20, default='completed')
    input_ref    = models.CharField(max_length=64, blank=True)   # hash → MemoryPayload
    output_ref   = models.CharField(max_length=64, blank=True)
    duration_ms  = models.IntegerField(null=True)
    retry_count  = models.IntegerField(default=0)
    error        = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'node_runs'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.node_code} [{self.status}] in {self.workflow_run_id}'


# ─── Human Action ─────────────────────────────────────────────────────────────

class HumanAction(models.Model):
    """
    Immutable record of every human decision in a workflow.
    Cannot be edited or deleted — tamper-evident audit record.
    """
    class ActionType(models.TextChoices):
        APPROVED  = 'APPROVED',  'Approved'
        REJECTED  = 'REJECTED',  'Rejected'
        ESCALATED = 'ESCALATED', 'Escalated'

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_run = models.ForeignKey(WorkflowRun, on_delete=models.CASCADE, related_name='human_actions')
    node_code    = models.CharField(max_length=100)          # which HITL node
    actor        = models.CharField(max_length=255)          # email of reviewer
    action       = models.CharField(max_length=20, choices=ActionType.choices)
    reason_code  = models.CharField(max_length=100, blank=True)
    justification = models.TextField(blank=True)
    timestamp    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'human_actions'
        ordering = ['timestamp']

    def save(self, *args, **kwargs):
        # Immutable — block updates after creation
        if self.pk:
            raise ValueError('HumanAction records are immutable and cannot be updated.')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.actor} → {self.action} on {self.node_code}'


# ─── Decision Point ───────────────────────────────────────────────────────────

class DecisionPoint(models.Model):
    """
    Structured evidence chain for every automated decision.
    The 'why' behind every choice the system made.
    """
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_run   = models.ForeignKey(WorkflowRun, on_delete=models.CASCADE, related_name='decisions')
    node_code      = models.CharField(max_length=100)
    options        = models.JSONField(default=list)          # options that were generated
    selected       = models.JSONField(default=dict)          # option that was chosen
    decision_basis = models.TextField(blank=True)            # why this option was selected
    quality_signals = models.JSONField(default=dict)         # confidence, completeness, etc.
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'decision_points'
        ordering = ['created_at']


# ─── Memory Payload ───────────────────────────────────────────────────────────

class MemoryPayload(models.Model):
    """
    Content-addressed blob store for node inputs/outputs.
    Referenced by hash — never inlined in audit records.
    """
    class PIIClass(models.TextChoices):
        NONE     = 'none',     'No PII'
        LOW      = 'low',      'Low sensitivity'
        HIGH     = 'high',     'High sensitivity'
        CRITICAL = 'critical', 'Critical / regulated PII'

    content_hash   = models.CharField(max_length=64, unique=True, primary_key=True)
    content        = models.JSONField()
    schema_version = models.CharField(max_length=20, default='1.0')
    pii_class      = models.CharField(max_length=20, choices=PIIClass.choices, default=PIIClass.NONE)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'memory_payloads'

    def __str__(self):
        return f'payload:{self.content_hash[:12]} [{self.pii_class}]'