# domains/manufacturing/models.py

import uuid
from django.db import models
from core.models import TenantAwareModel


class Batch(TenantAwareModel):
    """
    Manufacturing batch or production run.
    """
    class BatchStatus(models.TextChoices):
        PENDING    = 'pending',    'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED  = 'completed',  'Completed'
        FAILED     = 'failed',     'Failed'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_ref       = models.CharField(max_length=100)
    product_name    = models.CharField(max_length=255)
    quantity        = models.IntegerField()
    status          = models.CharField(max_length=20, choices=BatchStatus.choices, default=BatchStatus.PENDING)
    start_date      = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    line_number     = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'batches'
        unique_together = ('tenant', 'batch_ref')

    def __str__(self):
        return f'{self.batch_ref} — {self.product_name}'


class QualityInspection(TenantAwareModel):
    """
    Quality control inspection record.
    """
    class InspectionStatus(models.TextChoices):
        PASS  = 'pass',  'Pass'
        FAIL  = 'fail',  'Fail'
        HOLD  = 'hold',  'Hold for Review'

    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch             = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='inspections')
    inspection_date   = models.DateField()
    inspector_name    = models.CharField(max_length=255)
    status            = models.CharField(max_length=20, choices=InspectionStatus.choices, default=InspectionStatus.PASS)
    defects_found     = models.IntegerField(default=0)
    defect_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    notes             = models.TextField(blank=True)

    class Meta:
        db_table = 'quality_inspections'
        ordering = ['-inspection_date']

    def __str__(self):
        return f'{self.batch.batch_ref} — {self.status}'


class DefectRecord(TenantAwareModel):
    """
    Individual defect record from quality inspection.
    """
    class DefectSeverity(models.TextChoices):
        CRITICAL = 'critical', 'Critical'
        MAJOR    = 'major',    'Major'
        MINOR    = 'minor',    'Minor'

    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inspection        = models.ForeignKey(QualityInspection, on_delete=models.CASCADE, related_name='defects')
    defect_code       = models.CharField(max_length=50)
    description       = models.TextField()
    severity          = models.CharField(max_length=20, choices=DefectSeverity.choices)
    location          = models.CharField(max_length=255)
    remediation_note  = models.TextField(blank=True)

    class Meta:
        db_table = 'defect_records'

    def __str__(self):
        return f'{self.defect_code} — {self.get_severity_display()}'
