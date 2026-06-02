# domains/government/models.py

import uuid
from django.db import models
from core.models import TenantAwareModel


class Tender(TenantAwareModel):
    """
    Government procurement tender.
    """
    class TenderStatus(models.TextChoices):
        DRAFT        = 'draft',        'Draft'
        PUBLISHED    = 'published',    'Published'
        CLOSED       = 'closed',       'Closed'
        AWARDED      = 'awarded',      'Awarded'
        CANCELLED    = 'cancelled',    'Cancelled'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tender_ref      = models.CharField(max_length=100)
    title           = models.CharField(max_length=255)
    description     = models.TextField()
    status          = models.CharField(max_length=20, choices=TenderStatus.choices, default=TenderStatus.DRAFT)
    budget_amount   = models.DecimalField(max_digits=18, decimal_places=2)
    publication_date = models.DateField()
    closing_date    = models.DateField()
    award_date      = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'tenders'
        unique_together = ('tenant', 'tender_ref')

    def __str__(self):
        return f'{self.tender_ref} — {self.title}'


class Bidder(TenantAwareModel):
    """
    Bidder or vendor participating in a tender.
    """
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tender          = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='bidders')
    bidder_name     = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100)
    email           = models.EmailField()
    phone           = models.CharField(max_length=20)
    is_qualified    = models.BooleanField(default=True)

    class Meta:
        db_table = 'bidders'
        unique_together = ('tenant', 'tender', 'registration_number')

    def __str__(self):
        return f'{self.bidder_name} — {self.tender.tender_ref}'


class ProcurementRecord(TenantAwareModel):
    """
    Procurement transaction record.
    """
    class RecordType(models.TextChoices):
        TENDER      = 'tender',      'Tender'
        QUOTATION   = 'quotation',   'Quotation'
        EMERGENCY   = 'emergency',   'Emergency Purchase'
        RATE_CONTRACT = 'rate_contract', 'Rate Contract'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tender          = models.ForeignKey(Tender, on_delete=models.SET_NULL, null=True, blank=True)
    bidder          = models.ForeignKey(Bidder, on_delete=models.PROTECT, null=True, blank=True)
    record_type     = models.CharField(max_length=20, choices=RecordType.choices, default=RecordType.TENDER)
    po_number       = models.CharField(max_length=100)
    amount          = models.DecimalField(max_digits=18, decimal_places=2)
    order_date      = models.DateField()
    delivery_date   = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'procurement_records'
        unique_together = ('tenant', 'po_number')

    def __str__(self):
        return f'{self.po_number} — ₹{self.amount}'
