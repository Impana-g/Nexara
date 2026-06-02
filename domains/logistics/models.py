# domains/logistics/models.py

import uuid
from django.db import models
from core.models import TenantAwareModel


class Shipment(TenantAwareModel):
    """
    Shipment or cargo shipment record.
    """
    class ShipmentStatus(models.TextChoices):
        PENDING       = 'pending',       'Pending'
        IN_TRANSIT    = 'in_transit',    'In Transit'
        CLEARED       = 'cleared',       'Customs Cleared'
        DELIVERED     = 'delivered',     'Delivered'
        EXCEPTION     = 'exception',     'Exception'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment_ref    = models.CharField(max_length=100)
    origin          = models.CharField(max_length=255)
    destination     = models.CharField(max_length=255)
    status          = models.CharField(max_length=20, choices=ShipmentStatus.choices, default=ShipmentStatus.PENDING)
    shipped_date    = models.DateField()
    expected_delivery = models.DateField()
    actual_delivery = models.DateField(null=True, blank=True)
    total_weight_kg = models.DecimalField(max_digits=18, decimal_places=2)
    value_amount    = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        db_table = 'shipments'
        unique_together = ('tenant', 'shipment_ref')

    def __str__(self):
        return f'{self.shipment_ref} — {self.origin} to {self.destination}'


class CustomsRecord(TenantAwareModel):
    """
    Customs clearance and compliance record.
    """
    class ClearanceStatus(models.TextChoices):
        PENDING      = 'pending',      'Pending'
        CLEARED      = 'cleared',      'Cleared'
        HELD         = 'held',         'Held for Inspection'
        REJECTED     = 'rejected',     'Rejected'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment        = models.OneToOneField(Shipment, on_delete=models.CASCADE, related_name='customs_record')
    customs_ref     = models.CharField(max_length=100)
    clearance_status = models.CharField(max_length=20, choices=ClearanceStatus.choices, default=ClearanceStatus.PENDING)
    declaration_date = models.DateField()
    clearance_date  = models.DateField(null=True, blank=True)
    duty_paid_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.0)
    notes           = models.TextField(blank=True)

    class Meta:
        db_table = 'customs_records'
        unique_together = ('tenant', 'customs_ref')

    def __str__(self):
        return f'{self.customs_ref} — {self.clearance_status}'


class CargoItem(TenantAwareModel):
    """
    Individual cargo item within a shipment.
    """
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment        = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='cargo_items')
    item_code       = models.CharField(max_length=100)
    description     = models.TextField()
    quantity        = models.IntegerField()
    unit            = models.CharField(max_length=20)
    weight_kg       = models.DecimalField(max_digits=18, decimal_places=2)
    hs_code         = models.CharField(max_length=20, blank=True)  # Harmonized System code
    declared_value  = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        db_table = 'cargo_items'
        ordering = ['item_code']

    def __str__(self):
        return f'{self.item_code} — {self.description}'
