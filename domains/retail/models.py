# domains/retail/models.py

import uuid
from django.db import models
from core.models import TenantAwareModel


class Vendor(TenantAwareModel):
    """
    Vendor or supplier record in retail.
    """
    class VerificationStatus(models.TextChoices):
        PENDING    = 'pending',    'Pending'
        APPROVED   = 'approved',   'Approved'
        REJECTED   = 'rejected',   'Rejected'
        SUSPENDED  = 'suspended',  'Suspended'

    id                  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor_ref          = models.CharField(max_length=100)
    business_name       = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100)
    gst_number          = models.CharField(max_length=20, blank=True)
    email               = models.EmailField()
    phone               = models.CharField(max_length=20)
    verification_status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.PENDING)
    onboarded_date      = models.DateField()
    tenant              = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='retail_vendors')

    class Meta:
        db_table = 'vendors'
        unique_together = ('tenant', 'vendor_ref')

    def __str__(self):
        return f'{self.vendor_ref} — {self.business_name}'


class ReturnRequest(TenantAwareModel):
    """
    Customer return request record.
    """
    class ReturnStatus(models.TextChoices):
        INITIATED  = 'initiated',  'Initiated'
        ACCEPTED   = 'accepted',   'Accepted'
        PROCESSING = 'processing', 'Processing'
        COMPLETED  = 'completed',  'Completed'
        REJECTED   = 'rejected',   'Rejected'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    return_ref      = models.CharField(max_length=100)
    vendor          = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='return_requests')
    order_reference = models.CharField(max_length=100)
    reason          = models.TextField()
    status          = models.CharField(max_length=20, choices=ReturnStatus.choices, default=ReturnStatus.INITIATED)
    requested_date  = models.DateField()
    resolved_date   = models.DateField(null=True, blank=True)
    refund_amount   = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'return_requests'
        unique_together = ('tenant', 'return_ref')

    def __str__(self):
        return f'{self.return_ref} — {self.status}'


class GSTRecord(TenantAwareModel):
    """
    GST (Goods and Services Tax) compliance record.
    """
    class RecordType(models.TextChoices):
        INWARD      = 'inward',      'Inward Supply'
        OUTWARD     = 'outward',     'Outward Supply'
        ADJUSTMENT  = 'adjustment',  'Adjustment'
        RETURN      = 'return',      'Return/Reversal'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor          = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='gst_records')
    record_type     = models.CharField(max_length=20, choices=RecordType.choices)
    invoice_ref     = models.CharField(max_length=100)
    transaction_date = models.DateField()
    taxable_amount  = models.DecimalField(max_digits=18, decimal_places=2)
    gst_rate_percent = models.DecimalField(max_digits=5, decimal_places=2)
    gst_amount      = models.DecimalField(max_digits=18, decimal_places=2)
    hsn_code        = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'gst_records'
        unique_together = ('tenant', 'invoice_ref')

    def __str__(self):
        return f'{self.invoice_ref} — ₹{self.gst_amount}'
