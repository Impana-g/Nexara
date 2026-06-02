# domains/insurance/models.py

import uuid
from django.db import models
from core.models import TenantAwareModel


class Policy(TenantAwareModel):
    """
    Insurance policy record.
    """
    class PolicyType(models.TextChoices):
        MOTOR     = 'motor',     'Motor Insurance'
        HEALTH    = 'health',    'Health Insurance'
        LIFE      = 'life',      'Life Insurance'
        PROPERTY  = 'property',  'Property Insurance'
        TRAVEL    = 'travel',    'Travel Insurance'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy_number   = models.CharField(max_length=100)
    policy_type     = models.CharField(max_length=20, choices=PolicyType.choices)
    holder_name     = models.CharField(max_length=255)
    premium_amount  = models.DecimalField(max_digits=18, decimal_places=2)
    start_date      = models.DateField()
    end_date        = models.DateField()
    is_active       = models.BooleanField(default=True)

    class Meta:
        db_table = 'policies'
        unique_together = ('tenant', 'policy_number')

    def __str__(self):
        return f'{self.policy_number} — {self.holder_name}'


class Claim(TenantAwareModel):
    """
    Insurance claim against a policy.
    """
    class ClaimStatus(models.TextChoices):
        FILED      = 'filed',      'Filed'
        UNDER_REVIEW = 'review',   'Under Review'
        APPROVED   = 'approved',   'Approved'
        REJECTED   = 'rejected',   'Rejected'
        SETTLED    = 'settled',    'Settled'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy          = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='claims')
    claim_number    = models.CharField(max_length=100)
    claim_amount    = models.DecimalField(max_digits=18, decimal_places=2)
    status          = models.CharField(max_length=20, choices=ClaimStatus.choices, default=ClaimStatus.FILED)
    filed_date      = models.DateField()
    settlement_date = models.DateField(null=True, blank=True)
    description     = models.TextField()

    class Meta:
        db_table = 'claims'
        unique_together = ('tenant', 'claim_number')

    def __str__(self):
        return f'{self.claim_number} — ₹{self.claim_amount}'


class FraudFlag(TenantAwareModel):
    """
    Fraud detection and flagging record.
    """
    class SeverityLevel(models.TextChoices):
        LOW      = 'low',      'Low'
        MEDIUM   = 'medium',   'Medium'
        HIGH     = 'high',     'High'
        CRITICAL = 'critical', 'Critical'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    claim           = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='fraud_flags')
    flag_reason     = models.TextField()
    severity        = models.CharField(max_length=20, choices=SeverityLevel.choices, default=SeverityLevel.LOW)
    flagged_date    = models.DateTimeField(auto_now_add=True)
    resolved_date   = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(blank=True)

    class Meta:
        db_table = 'fraud_flags'
        ordering = ['-flagged_date']

    def __str__(self):
        return f'{self.claim.claim_number} — {self.get_severity_display()}'


class Settlement(TenantAwareModel):
    """
    Settlement details for a claim.
    """
    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    claim             = models.OneToOneField(Claim, on_delete=models.CASCADE, related_name='settlement')
    settlement_amount = models.DecimalField(max_digits=18, decimal_places=2)
    settled_date      = models.DateField()
    payment_method    = models.CharField(max_length=100, blank=True)
    reference_number  = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'settlements'

    def __str__(self):
        return f'{self.claim.claim_number} — ₹{self.settlement_amount}'
