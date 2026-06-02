# domains/energy/models.py

import uuid
from django.db import models
from core.models import TenantAwareModel


class ESGReport(TenantAwareModel):
    """
    Environmental, Social, Governance (ESG) report.
    """
    class ReportType(models.TextChoices):
        ANNUAL         = 'annual',         'Annual'
        QUARTERLY      = 'quarterly',      'Quarterly'
        SUSTAINABILITY = 'sustainability', 'Sustainability'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_ref      = models.CharField(max_length=100)
    report_type     = models.CharField(max_length=20, choices=ReportType.choices)
    reporting_period = models.CharField(max_length=50)
    environmental_score = models.IntegerField(default=50)  # 0-100
    social_score    = models.IntegerField(default=50)      # 0-100
    governance_score = models.IntegerField(default=50)     # 0-100
    published_date  = models.DateField()
    document_url    = models.URLField(blank=True)

    class Meta:
        db_table = 'esg_reports'
        unique_together = ('tenant', 'report_ref')

    def __str__(self):
        return f'{self.report_ref} — {self.reporting_period}'


class EmissionRecord(TenantAwareModel):
    """
    Carbon and greenhouse gas emission records.
    """
    class EmissionType(models.TextChoices):
        CO2  = 'co2',  'CO2'
        CH4  = 'ch4',  'CH4 (Methane)'
        N2O  = 'n2o',  'N2O (Nitrous Oxide)'
        OTHER = 'other', 'Other'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report          = models.ForeignKey(ESGReport, on_delete=models.CASCADE, related_name='emissions')
    emission_type   = models.CharField(max_length=20, choices=EmissionType.choices)
    quantity_tonnes = models.DecimalField(max_digits=18, decimal_places=2)
    measurement_date = models.DateField()
    source          = models.CharField(max_length=255)
    notes           = models.TextField(blank=True)

    class Meta:
        db_table = 'emission_records'
        ordering = ['-measurement_date']

    def __str__(self):
        return f'{self.emission_type} — {self.quantity_tonnes}T'


class CarbonCredit(TenantAwareModel):
    """
    Carbon credit or offset record.
    """
    class CreditStatus(models.TextChoices):
        ISSUED      = 'issued',      'Issued'
        ACTIVE      = 'active',      'Active'
        RETIRED     = 'retired',     'Retired'
        CANCELLED   = 'cancelled',   'Cancelled'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    credit_ref      = models.CharField(max_length=100)
    quantity_tonnes = models.DecimalField(max_digits=18, decimal_places=2)
    status          = models.CharField(max_length=20, choices=CreditStatus.choices, default=CreditStatus.ISSUED)
    issue_date      = models.DateField()
    expiry_date     = models.DateField(null=True, blank=True)
    project_name    = models.CharField(max_length=255)
    verification_url = models.URLField(blank=True)

    class Meta:
        db_table = 'carbon_credits'
        unique_together = ('tenant', 'credit_ref')

    def __str__(self):
        return f'{self.credit_ref} — {self.quantity_tonnes}T'
