# domains/legal/models.py

import uuid
from django.db import models
from core.models import TenantAwareModel


class Contract(TenantAwareModel):
    """
    Legal contract record.
    """
    class Status(models.TextChoices):
        DRAFT      = 'draft',      'Draft'
        ACTIVE     = 'active',     'Active'
        TERMINATED = 'terminated', 'Terminated'
        ARCHIVED   = 'archived',   'Archived'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract_ref    = models.CharField(max_length=100)
    title           = models.CharField(max_length=255)
    description     = models.TextField(blank=True)
    status          = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    start_date      = models.DateField()
    end_date        = models.DateField(null=True, blank=True)
    is_active       = models.BooleanField(default=True)

    class Meta:
        db_table = 'contracts'
        unique_together = ('tenant', 'contract_ref')

    def __str__(self):
        return f'{self.contract_ref} — {self.title}'


class Case(TenantAwareModel):
    """
    Legal case record.
    """
    class Status(models.TextChoices):
        OPEN       = 'open',       'Open'
        CLOSED     = 'closed',     'Closed'
        SETTLED    = 'settled',    'Settled'
        PENDING    = 'pending',    'Pending'

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case_ref     = models.CharField(max_length=100)
    title        = models.CharField(max_length=255)
    description  = models.TextField(blank=True)
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    filing_date  = models.DateField()
    is_active    = models.BooleanField(default=True)

    class Meta:
        db_table = 'cases'
        unique_together = ('tenant', 'case_ref')

    def __str__(self):
        return f'{self.case_ref} — {self.title}'


class Filing(TenantAwareModel):
    """
    Court filing associated with a case.
    """
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case         = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='filings')
    filing_type  = models.CharField(max_length=100)
    filing_date  = models.DateField()
    document_url = models.URLField(blank=True)
    notes        = models.TextField(blank=True)

    class Meta:
        db_table = 'filings'
        ordering = ['-filing_date']

    def __str__(self):
        return f'{self.filing_type} for {self.case.case_ref}'


class ConflictRecord(TenantAwareModel):
    """
    Conflict of interest or compliance record.
    """
    class ConflictType(models.TextChoices):
        CONFLICT_OF_INTEREST = 'coi',       'Conflict of Interest'
        COMPLIANCE_BREACH    = 'breach',    'Compliance Breach'
        REGULATORY_ISSUE     = 'regulatory','Regulatory Issue'

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conflict_ref = models.CharField(max_length=100)
    conflict_type = models.CharField(max_length=20, choices=ConflictType.choices)
    description  = models.TextField()
    severity     = models.IntegerField(default=50)  # 0-100
    resolved_at  = models.DateTimeField(null=True, blank=True)
    is_active    = models.BooleanField(default=True)

    class Meta:
        db_table = 'conflict_records'
        unique_together = ('tenant', 'conflict_ref')

    def __str__(self):
        return f'{self.conflict_ref} — {self.get_conflict_type_display()}'
