# domains/it/models.py

import uuid
from django.db import models
from core.models import TenantAwareModel


# ─── Change Request (RFC) ─────────────────────────────────────────────────────

class ChangeRequest(TenantAwareModel):
    """
    Request for Change (RFC) — a production change submission.
    e.g. deploying a hotfix, infrastructure change, config update.
    """
    class RiskLevel(models.TextChoices):
        LOW      = 'low',      'Low'
        MEDIUM   = 'medium',   'Medium'
        HIGH     = 'high',     'High'
        CRITICAL = 'critical', 'Critical'

    class Status(models.TextChoices):
        DRAFT     = 'draft',     'Draft'
        SUBMITTED = 'submitted', 'Submitted'
        APPROVED  = 'approved',  'Approved'
        REJECTED  = 'rejected',  'Rejected'
        DEPLOYED  = 'deployed',  'Deployed'

    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title            = models.CharField(max_length=255)
    description      = models.TextField()
    affected_system  = models.CharField(max_length=255)
    rollback_plan    = models.TextField()
    deployment_window = models.DateTimeField()
    risk_level       = models.CharField(max_length=20, choices=RiskLevel.choices, default=RiskLevel.MEDIUM)
    status           = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    submitted_by     = models.CharField(max_length=255)
    ingestion_batch_id = models.CharField(max_length=64, blank=True)

    class Meta:
        db_table = 'it_change_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} [{self.risk_level}] — {self.status}'


# ─── Vendor ───────────────────────────────────────────────────────────────────

class Vendor(TenantAwareModel):
    """
    Software/service vendor record.
    """
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name         = models.CharField(max_length=255)
    contact_email = models.EmailField(blank=True)
    service_type = models.CharField(max_length=100)
    is_active    = models.BooleanField(default=True)
    tenant       = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='it_vendors')

    class Meta:
        db_table = 'it_vendors'

    def __str__(self):
        return self.name


# ─── Software License ─────────────────────────────────────────────────────────

class SoftwareLicense(TenantAwareModel):
    """
    Software license record with expiry tracking.
    """
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor       = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=255)
    license_key  = models.CharField(max_length=255, blank=True)
    seats        = models.IntegerField(default=1)
    expiry_date  = models.DateField()
    is_active    = models.BooleanField(default=True)

    class Meta:
        db_table = 'it_software_licenses'
        ordering = ['expiry_date']

    def __str__(self):
        return f'{self.product_name} — expires {self.expiry_date}'


# ─── Incident ─────────────────────────────────────────────────────────────────

class Incident(TenantAwareModel):
    """
    IT incident record — outages, security events, SLA breaches.
    """
    class Severity(models.TextChoices):
        P1 = 'p1', 'P1 — Critical'
        P2 = 'p2', 'P2 — High'
        P3 = 'p3', 'P3 — Medium'
        P4 = 'p4', 'P4 — Low'

    class Status(models.TextChoices):
        OPEN       = 'open',       'Open'
        MITIGATED  = 'mitigated',  'Mitigated'
        RESOLVED   = 'resolved',   'Resolved'

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title        = models.CharField(max_length=255)
    description  = models.TextField()
    severity     = models.CharField(max_length=5, choices=Severity.choices)
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    affected_system = models.CharField(max_length=255)
    reported_by  = models.CharField(max_length=255)
    resolved_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'it_incidents'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} [{self.severity}] — {self.status}'